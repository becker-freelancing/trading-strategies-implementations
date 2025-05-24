import numpy as np
import pandas as pd
import pandas_ta as ta

from zpython.util import split_on_gaps
from zpython.util import train_data


def add_trend(df):
    df = df.reset_index(drop=True)
    df.set_index("closeTime", inplace=True)

    df["EMA_50"] = ta.ema(df["closeBid"], 50)
    df["EMA_100"] = ta.ema(df["closeBid"], 100)

    shift = 15
    df["EMA_50_SLOPE"] = (df["EMA_50"] - df["EMA_50"].shift(shift)) / shift

    df["Trend"] = 0

    up = (df["EMA_50"] > df["EMA_100"]) & (df["EMA_50_SLOPE"] > -0.05)
    df.loc[up[up == True].index, "Trend"] = 1
    down = (df["EMA_50"] < df["EMA_100"]) & (df["EMA_50_SLOPE"] < 0.05)
    df.loc[down[down == True].index, "Trend"] = -1
    df.reset_index(inplace=True)
    return df


def add_vola(df):
    df = df.reset_index(drop=True)

    df["Return"] = np.log(df["closeBid"] / df["closeBid"].shift(1))
    df["volatility"] = df["Return"].rolling(window=30).std()

    high_thres = df["volatility"].quantile(0.5)

    high = df["volatility"] > high_thres
    low = df["volatility"] < high_thres
    df["vol_class"] = 0
    df.loc[high[high == True].index, "vol_class"] = 1
    df.loc[low[low == True].index, "vol_class"] = -1

    return df


def statistic(df):
    for vol in [-1, 1]:
        for trend in [-1, 0, 1]:
            print("VOLA: ", vol)
            print("TREND: ", trend)
            slice = df[(df["Trend"] == trend) & (df["vol_class"] == vol)]
            print("\t Percent of all: ", (len(slice) / len(df)) * 100)


all = train_data()
dfs = split_on_gaps(all, 1)
mapped = [add_trend(add_vola(df)) for df in dfs]
parsed = pd.concat(mapped)

statistic(parsed)
