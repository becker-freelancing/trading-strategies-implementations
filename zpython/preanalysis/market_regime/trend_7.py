import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pandas_ta as ta

from zpython.util import train_data
import numpy as np
import warnings
from zpython.util import split_on_gaps

warnings.filterwarnings('ignore')

print("Read data")
df = train_data()
print("Create indicators")
dfs = split_on_gaps(df, 1)
for df in dfs:
    df = df.reset_index(drop=True)
    df.set_index("closeTime", inplace=True)
    df["closeBid5Min"] = df.resample(f'5min').agg({
        "closeBid": "last"
    })["closeBid"]

    df["EMA_200"] = ta.ema(df["closeBid5Min"].dropna(), 200)
    df["EMA_150"] = ta.ema(df["closeBid"], 150)
    df["EMA_20"] = ta.ema(df["closeBid"], 20)
    df["EMA_50"] = ta.ema(df["closeBid"], 50)
    df["ADX"] = ta.adx(df["highBid"], df["lowBid"], df["closeBid"], length=14)["ADX_14"]

    shift = 15
    df["EMA_50_SLOPE"] = (df["EMA_50"] - df["EMA_50"].shift(shift)) / shift
    df["EMA_200_SLOPE"] = (df["EMA_200"] - df["EMA_200"].shift(shift)) / shift
    df["EMA_150_SLOPE"] = (df["EMA_150"] - df["EMA_150"].shift(shift)) / shift
    df["EMA_50_FLAT"] = abs(df["EMA_50_SLOPE"]) < 0.05

    df["Trend"] = 0

    up = (df["EMA_200_SLOPE"] > 0.0)
    df["Trend"].loc[up[up == True].index] = 1
    down = (df["EMA_200_SLOPE"] < -0.0)
    df["Trend"].loc[down[down == True].index] = -1
    #
    # def smooth(x):
    #     side_count = len(np.where(x.values == 0)[0])
    #     if side_count > 2:
    #         return 0
    #     return x[x.index.max()]
    # df["Trend"] = df["Trend"].rolling(window=5).apply(smooth)
    side = ~(up | down)

    df = df.dropna()
    df["color"] = df["Trend"].map({1: "green", 0: "black", -1: "red"})

    plt.scatter(df.index, df["closeBid"], label="Close", c=df["color"])
    plt.plot(df.index, df["EMA_200"], label="EMA(200)")
    plt.plot(df.index, df["EMA_150"], label="EMA(150)")
    plt.plot(df.index, df["EMA_20"], label="EMA(20)")
    plt.plot(df.index, df["EMA_50"], label="EMA(50)")
    v = np.min(df["closeBid"]) - 30
    plt.plot(df.index, df["ADX"] + v, label="ADX")
    plt.plot(df.index, [v] * len(df.index), label="ADX Base Line")
    plt.plot(df.index, [v + 20] * len(df.index), label="ADX > 20")
    plt.legend()
    plt.show()
