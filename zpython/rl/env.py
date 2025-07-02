import collections
import random

import gymnasium as gym
import gymnasium.spaces as spaces
import numpy as np
import pandas as pd

from zpython.rl.scaler import Scaler
from zpython.rl.statistics_recorder import StatisticsRecorder


class TradingEnv(gym.Env):
    def __init__(self,
                 data: pd.DataFrame,
                 episode_max_len: int,
                 lookback_window_len: int,
                 train_start: int,
                 train_end: int,
                 test_start: int,
                 test_end: int,
                 leverage: float = 10.,
                 order_size: float = 50.,
                 initial_capital: float = 5000.,
                 open_fee: float = 10e-4,
                 close_fee: float = 10e-4,
                 maintenance_margin_percentage: float = 0.012,
                 initial_random_allocated: float = 0,
                 regime: str = 'training',
                 record_stats: bool = True,
                 ):
        self.scaler = Scaler(min_quantile=0.5, max_quantile=99.5, scale_coef=initial_capital)
        self.leverage = leverage
        self.episode_max_len = episode_max_len
        self.lookback_window_len = lookback_window_len
        self.order_size = order_size
        self.initial_balance = initial_capital
        self.available_balance = initial_capital
        self.wallet_balance = initial_capital
        self.open_fee = open_fee
        self.close_fee = close_fee
        self.maintenance_margin_percentage = maintenance_margin_percentage
        self.initial_random_allocated = initial_random_allocated
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end
        self.regime = regime
        self.record_stats = record_stats
        self.price = data["ETHPERP_1_closeBid"].values.reshape(-1, 1)
        self.data_df = data
        self.data = data.values
        self.observation_dim = (data.shape[1] + 2) * lookback_window_len
        self.reward_realized_pnl_short = 0.
        self.reward_realized_pnl_long = 0.

        self.liquidation = False
        self.episode_maxstep_achieved = False
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim,), dtype=np.float64)
        self.action_space = spaces.Discrete(4)

        if self.regime == "training":
            self.max_step = self.episode_max_len - 1
            self.time_absolute = random.randint(
                self.train_start + self.lookback_window_len * 4 + 24,  # +24 für random init positions
                self.train_end - self.episode_max_len - 1
            )
        elif self.regime == "evaluation":
            self.max_step = self.episode_max_len - 1  # self.test_end[random_interval] - self.test_start[random_interval] - 1
            self.time_absolute = random.randint(
                self.test_start + self.lookback_window_len * 4 + 24,  # +24 für random init positions
                self.test_end - self.episode_max_len - 1
            )

        self._reset_env_state()

    def reset(self, seed=7, options={}):
        self._reset_env_state()
        state_array, reset_array = self._get_observation_reset()
        scaled_obs_reset = self.scaler.reset(state_array, reset_array).flatten()

        # return scaled_obs_reset
        return scaled_obs_reset, {}

    def _get_observation_reset(self):
        for current_time_absolute in range(self.time_absolute - self.lookback_window_len * 4, self.time_absolute):
            self._get_observation_step(current_time_absolute)

        return np.array(self.state_que), np.array(self.reset_que)

    def _get_observation_step(self, current_time):
        input_array = self.data[current_time]

        day_column = input_array[0]
        hour_column = input_array[1]
        available_balance = self.available_balance
        unrealized_pnl = self.unrealized_pnl_long + self.unrealized_pnl_short

        current_observation = np.hstack(
            (day_column, hour_column, available_balance, unrealized_pnl, input_array[2:])).astype(np.float32)
        self.state_que.append(current_observation)
        self.reset_que.append(current_observation)

        return np.array(self.state_que)

    def _reset_env_state_short(self, random_open_position):
        # Start episode with already open SHORT position
        if self.regime == "training" and random_open_position:
            # sample average_price from past 24 hours
            self.average_price_short = random.uniform(self.price[self.time_absolute - 24, 0],
                                                      self.price[self.time_absolute, 0])
            self.position_value_short = random.uniform(0., self.initial_random_allocated)
            self.coins_short = self.position_value_short / self.average_price_short * (-1)
        else:
            self.average_price_short = self.price[self.time_absolute, 0]
            self.position_value_short = 0.
            self.coins_short = 0.

    def _reset_env_state_long(self, random_open_position):
        # Start episode with already open LONG position
        if self.regime == "training" and random_open_position:
            # sample average_price from past 24 hours
            self.average_price_long = random.uniform(self.price[self.time_absolute - 24, 0],
                                                     self.price[self.time_absolute, 0])
            self.position_value_long = random.uniform(0., self.initial_random_allocated)
            self.coins_long = self.position_value_long / self.average_price_long
        else:
            self.average_price_long = self.price[self.time_absolute, 0]
            self.position_value_long = 0.
            self.coins_long = 0.

    def _reset_env_state(self):
        self.statistics_recorder = StatisticsRecorder(record_statistics=self.record_stats)
        self.state_que = collections.deque(maxlen=self.lookback_window_len)
        self.reset_que = collections.deque(
            maxlen=self.lookback_window_len * 4)  # dataframe to fit scaler is 4 times longer than lookback_window_len

        self.time_relative = 0  # steps played in the current episode
        self.wallet_balance = self.initial_balance

        self.liquidation = False
        self.episode_maxstep_achieved = False

        # fixed bid/ask spread
        self.price_bid = self.price[self.time_absolute, 0] * (1 - self.open_fee)
        self.price_ask = self.price[self.time_absolute, 0] * (1 + self.open_fee)

        # open position at the episode start can be only long or only short
        random_initial_position = random.choice([True, False])  # used if self.initial_random_allocated > 0
        self._reset_env_state_short(random_initial_position)
        self._reset_env_state_long(not random_initial_position)  # invert random_initial_position

        self.margin_short, self.margin_long = self._calculate_margin_isolated()

        self.available_balance = max(self.wallet_balance - self.margin_short - self.margin_long, 0)

        if self.regime == "training":
            self.max_step = self.episode_max_len - 1
            # Episode beginning random sampling
            self.time_absolute = random.randint(
                self.train_start + self.lookback_window_len * 4 + 24,  # +24 für random init positions
                self.train_end - self.episode_max_len - 1
            )
        elif self.regime == "evaluation":
            self.max_step = self.episode_max_len - 1  # self.test_end[random_interval] - self.test_start[random_interval] - 1
            self.time_absolute = random.randint(
                self.test_start + self.lookback_window_len * 4 + 24,  # +24 für random init positions
                self.test_end - self.episode_max_len - 1
            )

        self.unrealized_pnl_short = (
                -self.coins_short * (self.average_price_short - self.price_ask))  # - self.fee_to_close_short
        self.unrealized_pnl_long = (
                self.coins_long * (self.price_bid - self.average_price_long))  # - self.fee_to_close_long

        # equity at the episode's beginning
        self.equity = self.wallet_balance + self.unrealized_pnl_short + self.unrealized_pnl_long

    def _calculate_margin_isolated(self):
        self.position_value_short = -self.coins_short * self.average_price_short
        self.position_value_long = self.coins_long * self.average_price_long

        self.initial_margin_short = self.position_value_short / self.leverage
        self.initial_margin_long = self.position_value_long / self.leverage

        self.fee_to_close_short = self.position_value_short * self.close_fee
        self.fee_to_close_long = self.position_value_long * self.close_fee

        self.margin_short = self.initial_margin_short + self.maintenance_margin_percentage * self.position_value_short + self.fee_to_close_short
        self.margin_long = self.initial_margin_long + self.maintenance_margin_percentage * self.position_value_long + self.fee_to_close_long

        return self.margin_short, self.margin_long

    def step(self, action: int):
        assert action in [0, 1, 2, 3], action

        # price = self.price_array[self.time_absolute, 0]
        self.price_bid = self.price[self.time_absolute, 0] * (1 - self.open_fee)
        self.price_ask = self.price[self.time_absolute, 0] * (1 + self.open_fee)

        margin_short_start = self.margin_short
        margin_long_start = self.margin_long

        self.reward_realized_pnl_short = 0.
        self.reward_realized_pnl_long = 0.

        # Oneway actions
        if action == 0:  # do nothing
            self.reward_realized_pnl_long = 0.
            self.reward_realized_pnl_short = 0.

        # similar to "BUY" button
        if action == 1:  # open/increace long position by self.order_size
            if self.coins_long >= 0:
                if self.available_balance > self.order_size:
                    buy_num_coins = self.order_size / self.price_ask
                    self.average_price_long = (self.position_value_long + buy_num_coins * self.price_ask) / (
                            self.coins_long + buy_num_coins)
                    self.initial_margin_long += buy_num_coins * self.price_ask / self.leverage
                    self.coins_long += buy_num_coins

        # similar to "SELL" button
        if action == 2:  # close/reduce long position by self.order_size
            if self.coins_long > 0:
                sell_num_coins = min(self.coins_long, self.order_size / self.price_ask)
                self.initial_margin_long *= (max((self.coins_long - sell_num_coins), 0.) / self.coins_long)
                self.coins_long = max(self.coins_long - sell_num_coins, 0)  # cannot be negative
                realized_pnl = sell_num_coins * (self.price_bid - self.average_price_long)
                self.wallet_balance += realized_pnl
                self.reward_realized_pnl_long = realized_pnl

        self.liquidation = -self.unrealized_pnl_long - self.unrealized_pnl_short > self.margin_long + self.margin_short
        self.episode_maxstep_achieved = self.time_relative == self.max_step

        # CLOSE entire position or LIQUIDATION
        if action == 3 or self.liquidation or self.episode_maxstep_achieved:
            # close LONG position
            if self.coins_long > 0:
                sell_num_coins = self.coins_long
                # becomes zero
                self.initial_margin_long *= max((self.coins_long - sell_num_coins), 0.) / self.coins_long
                # becomes zero
                self.coins_long = max(self.coins_long - sell_num_coins, 0)
                realized_pnl = sell_num_coins * (self.price_bid - self.average_price_long)
                self.wallet_balance += realized_pnl
                self.reward_realized_pnl_long = realized_pnl

        self.margin_short, self.margin_long = self._calculate_margin_isolated()
        self.available_balance = max(self.wallet_balance - self.margin_short - self.margin_long, 0)
        self.unrealized_pnl_short = (
                -self.coins_short * (self.average_price_short - self.price_ask))  # self.coins_short is negatve
        self.unrealized_pnl_long = (
                self.coins_long * (self.price_bid - self.average_price_long))  # - self.fee_to_close_long
        next_equity = (self.wallet_balance + self.unrealized_pnl_short + self.unrealized_pnl_long)

        done = self.episode_maxstep_achieved or self.liquidation  # end of episode or liquidation event

        # reward function
        # normalize rewards to fit [-10:10] range
        reward = (self.reward_realized_pnl_short + self.reward_realized_pnl_long) / self.initial_balance

        self.equity = next_equity

        margin_short_end = self.margin_short
        margin_long_end = self.margin_long

        obs_step = self._get_observation_step(self.time_absolute)
        obs = self.scaler.step(obs_step).flatten()

        info = {"action": action,
                "reward": reward,
                "reward_realized_pnl_short": self.reward_realized_pnl_short,
                "reward_realized_pnl_long": self.reward_realized_pnl_long,
                "unrealized_pnl_short": self.unrealized_pnl_short,
                "unrealized_pnl_long": self.unrealized_pnl_long,
                "margin_short_start": margin_short_start,
                "margin_long_start": margin_long_start,
                "margin_short_end": margin_short_end,
                "margin_long_end": margin_long_end,
                "num_steps": self.time_relative,
                "coins_short": self.coins_short,
                "coins_long": self.coins_long,
                "equity": self.equity,
                "wallet_balance": self.wallet_balance,
                "average_price_short": self.average_price_short,
                "average_price_long": self.average_price_long}

        self.statistics_recorder.update(
            action=action,
            reward=reward,
            reward_realized_pnl_short=self.reward_realized_pnl_short,
            reward_realized_pnl_long=self.reward_realized_pnl_long,
            unrealized_pnl_short=self.unrealized_pnl_short,
            unrealized_pnl_long=self.unrealized_pnl_long,
            margin_short_start=margin_short_start,
            margin_long_start=margin_long_start,
            margin_short_end=margin_short_end,
            margin_long_end=margin_long_end,
            num_steps=self.time_relative,
            coins_short=self.coins_short,
            coins_long=self.coins_long,
            equity=self.equity,
            wallet_balance=self.wallet_balance,
            average_price_short=self.average_price_short,
            average_price_long=self.average_price_long,
        )


        self.time_absolute += 1
        self.time_relative += 1

        return obs, reward, done, False, info
