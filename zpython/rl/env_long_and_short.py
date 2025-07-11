import collections
import random

import gymnasium as gym
import gymnasium.spaces as spaces
import numpy as np
import pandas as pd

from zpython.rl.scaler import Scaler
from zpython.rl.statistics_recorder import StatisticsRecorder


def compute_fee(volume: float, price: float, fee_rate: float) -> float:
    """
    Compute transaction fee based on volume (coins), price per coin, and fee rate.
    """
    return abs(volume) * price * fee_rate


class TradingEnvLongAndShort(gym.Env):
    """
    Gym environment for leveraged long/short trading with explicit fee handling,
    net position, and minimum hold time.
    """
    metadata = {"render.modes": ["human"]}

    def __init__(
            self,
            data: pd.DataFrame,
            episode_max_len: int,
            lookback_window_len: int,
            train_start: int,
            train_end: int,
            test_start: int,
            test_end: int,
            leverage: float = 10.0,
            order_size: float = 50.0,
            initial_capital: float = 5000.0,
            fee_rate: float = 0.000825,  # 0.055% * 1.5
            maintenance_margin_percentage: float = 0.012,
            regime: str = 'training',
            record_stats: bool = False,
            min_hold_steps: int = 3,
    ):
        # Core parameters
        self.data = data.values
        self.price_series = data['ETHPERP_1_closeBid'].values
        self.initial_balance = initial_capital
        self.leverage = leverage
        self.order_size = order_size
        self.fee_rate = fee_rate
        self.maintenance_margin = maintenance_margin_percentage
        self.episode_max_len = episode_max_len
        self.lookback_window_len = lookback_window_len
        self.train_start = train_start
        self.train_end = train_end
        self.test_start = test_start
        self.test_end = test_end
        self.regime = regime
        self.record_stats = record_stats
        self.min_hold_steps = min_hold_steps

        # State
        self.scaler = Scaler(min_quantile=0.5, max_quantile=99.5, scale_coef=initial_capital)
        self.statistics_recorder = None

        # Define spaces
        feature_dim = data.shape[1]
        self.observation_dim = (feature_dim + 2) * lookback_window_len
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(self.observation_dim,), dtype=np.float32)
        # Actions: 0 = hold, 1 = increase long, 2 = increase short, 3 = close all
        self.action_space = spaces.Discrete(4)

        self._reset_env_state()

    def reset(self, seed=None, options=None):
        self._reset_env_state()
        state, reset = self._get_observation_reset()
        obs = self.scaler.reset(state, reset).flatten()
        return obs, {}

    def _reset_env_state(self):
        # Episode iteration counters and balances
        self.time_relative = 0
        self.wallet_balance = self.initial_balance
        self.position_coins = 0.0  # net position: positive = long, negative = short
        self.avg_price = 0.0  # average entry price of current net position
        self.entry_step = 0

        # Random start in data
        if self.regime == 'training':
            start = self.train_start + self.lookback_window_len
            end = self.train_end - self.episode_max_len
        else:
            start = self.test_start + self.lookback_window_len
            end = self.test_end - self.episode_max_len
        self.time_absolute = random.randint(start, end)
        self.max_step = self.episode_max_len - 1

        # Prepare deques
        self.state_que = collections.deque(maxlen=self.lookback_window_len)
        self.reset_que = collections.deque(maxlen=self.lookback_window_len * 4)

        # Populate reset and state buffers
        for t in range(self.time_absolute - self.lookback_window_len * 4, self.time_absolute):
            obs = self._get_obs(t)
            self.reset_que.append(obs)
            if t >= self.time_absolute - self.lookback_window_len:
                self.state_que.append(obs)

        self.statistics_recorder = StatisticsRecorder(record_statistics=self.record_stats)

    def _get_obs(self, t):
        arr = self.data[t]
        day, hour = arr[0], arr[1]
        unrealized_pnl = self.position_coins * (self.price_series[t] - self.avg_price)
        return np.concatenate((
            [day, hour, self.wallet_balance, unrealized_pnl],
            arr[2:]
        )).astype(np.float32)

    def _get_observation_reset(self):
        return np.array(self.state_que), np.array(self.reset_que)

    def step(self, action):
        assert action in [0, 1, 2, 3], action
        price = self.price_series[self.time_absolute]
        realized_pnl = 0.0
        fee_cost = 0.0

        # 1) Hold
        if action == 0:
            pass

        # 2) Increase long
        elif action == 1:
            # If short exists, close it first
            if self.position_coins < 0:
                realized, fee = self._close_position(price)
                realized_pnl += realized
                fee_cost += fee
            # Open/increase long
            coins = self.order_size / price
            fee = compute_fee(coins, price, self.fee_rate)
            self.wallet_balance -= fee
            fee_cost += fee
            # update avg price
            total_value = self.position_coins * self.avg_price + coins * price
            self.position_coins += coins
            self.avg_price = total_value / self.position_coins
            self.entry_step = self.time_relative

        # 3) Increase short
        elif action == 2:
            if self.position_coins > 0:
                realized, fee = self._close_position(price)
                realized_pnl += realized
                fee_cost += fee
            coins = self.order_size / price
            fee = compute_fee(coins, price, self.fee_rate)
            self.wallet_balance -= fee
            fee_cost += fee
            total_value = self.position_coins * self.avg_price - coins * price
            self.position_coins -= coins
            self.avg_price = total_value / self.position_coins
            self.entry_step = self.time_relative

        # 4) Close all or forced
        elif action == 3:
            realized, fee = self._close_position(price)
            realized_pnl += realized
            fee_cost += fee

        # Compute margin and available balance
        position_value = abs(self.position_coins * price)
        initial_margin = position_value / self.leverage
        maintenance = self.maintenance_margin * position_value
        self.equity = self.wallet_balance + self.position_coins * (price - self.avg_price)
        self.margin = initial_margin + maintenance
        self.available_balance = max(self.equity - self.margin, 0)

        # Update time
        self.time_absolute += 1
        self.time_relative += 1

        # Compute reward (net realized PnL)
        self.reward = realized_pnl / self.initial_balance
        done = (self.time_relative >= self.max_step)

        # Next observation
        obs = self._get_obs(self.time_absolute)
        self.reset_que.append(obs)
        self.state_que.append(obs)
        obs = self.scaler.step(obs).flatten()

        info = {
            'realized_pnl': realized_pnl,
            'fee_cost': fee_cost,
            'position_coins': self.position_coins,
            'equity': self.equity,
            'margin': self.margin,
            'available_balance': self.available_balance
        }
        self.statistics_recorder.update(**info)

        return obs, self.reward, done, False, info

    def _close_position(self, price: float):
        """
        Close entire position at given price, return realized PnL and fee cost.
        """
        coins = self.position_coins
        gross_pnl = coins * (price - self.avg_price)
        fee = compute_fee(abs(coins), price, self.fee_rate)
        net_pnl = gross_pnl - fee
        # Mindesthaltedauer-Penalty
        if self.time_relative - self.entry_step < self.min_hold_steps:
            penalty = compute_fee(abs(coins), price, self.fee_rate)
            net_pnl -= penalty
            fee += penalty
        self.wallet_balance += net_pnl
        # reset position
        self.position_coins = 0.0
        self.avg_price = 0.0
        return net_pnl, fee

    def render(self, mode='human'):
        print(f"Step: {self.time_relative}, Balance: {self.wallet_balance:.2f}, "
              f"Position: {self.position_coins:.4f} @ {self.avg_price:.2f}")
