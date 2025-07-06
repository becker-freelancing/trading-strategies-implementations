from stable_baselines3 import PPO
from tqdm import tqdm

from zpython.rl.env_only_long import TradingEnvOnlyLong
from zpython.util.data_split import backtest_data
from zpython.util.path_util import from_relative_path


# Data Read definieren
def read_short_train_eth(time_frame):
    return backtest_data(1)


def read_short_train_eth_15(time_frame):
    return backtest_data(15)


def read_short_train_data_btc(time_frame):
    return backtest_data(1, "BTCPERP")


def read_short_train_data_btc_15(time_frame):
    return backtest_data(15, "BTCPERP")


from zpython.util.indicator_creator import create_indicators
from zpython.util.market_regime import market_regime_to_number
import pandas as pd


# Alle Lesen und mergen
def prepare_data(data_read_fn, time_frame, pair, with_close=False):
    data, _ = create_indicators(data_read_function=data_read_fn, time_frame=time_frame, with_close=with_close)
    data["regime"] = data["regime"].apply(market_regime_to_number)
    data.columns = [f"{pair}_{time_frame}_{c}" for c in data.columns]
    return data


def reindex(data, index):
    data = data.reindex(index).ffill()
    return data


import os


def add_times(data):
    data.insert(0, "minute", data.index.hour * 60 + data.index.minute)
    data.insert(0, "day", data.index.dayofweek)
    return data


def read_all():
    if os.path.exists("./merged_backtest.csv"):
        df = pd.read_csv("./merged_backtest.csv")
        df["closeTime"] = pd.to_datetime(df["closeTime"])
        df.set_index("closeTime", inplace=True)
        return df
    eth_1 = prepare_data(read_short_train_eth, 1, "ETHPERP", with_close=True)
    eth_15 = prepare_data(read_short_train_eth_15, 15, "ETHPERP")
    eth_15 = reindex(eth_15, eth_1.index)
    btc_1 = prepare_data(read_short_train_data_btc, 1, "BTCPERP")
    btc_15 = prepare_data(read_short_train_data_btc_15, 15, "BTCPERP")
    btc_15 = reindex(btc_15, eth_1.index)

    merged = pd.merge(eth_1, btc_1, how="outer", left_index=True, right_index=True)
    merged = pd.merge(merged, eth_15, how="left", left_index=True, right_index=True)
    merged = pd.merge(merged, btc_15, how="left", left_index=True, right_index=True)
    merged = add_times(merged)
    merged = merged.dropna()
    merged_copy = merged.copy()
    merged_copy.reset_index(inplace=True)
    merged_copy.to_csv("./merged_backtest.csv", index=False)
    return merged


import multiprocessing as mp

EPISODE_MAX_LEN = 1440
LOOKBACK_WINDOW_LEN = EPISODE_MAX_LEN

MODEL_PATH = from_relative_path("models-bybit/RL_ONLY_LONG/best_model.zip")
DATA = read_all()
DATA = DATA[~DATA.index.duplicated()]

time_absolute_range = list(range(LOOKBACK_WINDOW_LEN * 4 + 1, len(DATA)))


def run_inference(time_absolute):
    env = TradingEnvOnlyLong(
        DATA,
        EPISODE_MAX_LEN,
        LOOKBACK_WINDOW_LEN,
        0, 0, 0, len(DATA) - 1,
        regime="evaluation"
    )

    model = PPO.load(MODEL_PATH, device="cuda")  # CPU für parallele Nutzung

    time = DATA.iloc[time_absolute].name
    obs, _ = env.reset(options={"time_absolute": time_absolute + 1})
    action, _ = model.predict(obs, deterministic=True)

    return {"closeTime": time, "action": action}


if __name__ == "__main__":
    with mp.Pool(mp.cpu_count()) as pool:
        results = list(tqdm(pool.imap(run_inference, time_absolute_range), total=len(time_absolute_range)))

    pd.DataFrame(results).to_csv(from_relative_path("prediction-bybit/RL_ONLY_LONG.csv"), index=False)
