from zpython.util.data_split import train_data


# Data Read definieren
def read_short_train_eth(time_frame):
    return train_data(1).iloc[-800000:]


def read_short_train_eth_15(time_frame):
    return train_data(15).iloc[-800000:]


def read_short_train_data_btc(time_frame):
    return train_data(1, "BTCPERP").iloc[-800000:]


def read_short_train_data_btc_15(time_frame):
    return train_data(15, "BTCPERP").iloc[-800000:]


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
    if os.path.exists("./merged.csv"):
        df = pd.read_csv("./merged.csv")
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
    merged_copy.to_csv("./merged.csv", index=False)
    return merged
