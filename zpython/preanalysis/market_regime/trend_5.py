import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pandas_ta as ta

from zpython.util import train_data
import warnings
from zpython.util import split_on_gaps

warnings.filterwarnings('ignore')

print("Read data")
df = train_data()
print("Create indicators")

df = split_on_gaps(df, 1)[2]
df = df.reset_index(drop=True)

df["EMA_200"] = ta.ema(df["closeBid"], 200)
df["EMA_20"] = ta.ema(df["closeBid"], 20)
df["EMA_50"] = ta.ema(df["closeBid"], 50)
df["ADX"] = ta.adx(df["highBid"], df["lowBid"], df["closeBid"], length=14)["ADX_14"]
shift = 15
df["EMA_50_SLOPE"] = (df["EMA_50"] - df["EMA_50"].shift(shift)) / shift
df["EMA_200_SLOPE"] = (df["EMA_200"] - df["EMA_200"].shift(shift)) / shift
df["EMA_50_FLAT"] = abs(df["EMA_50_SLOPE"]) < 0.05

df["Trend"] = 0

up = (df["EMA_20"] > df["EMA_50"]) & (df["EMA_50"] > df["EMA_200"]) & ~(df["EMA_50_FLAT"]) | (df["EMA_200_SLOPE"] > 0.2)
df["Trend"].loc[up[up == True].index] = 1
down = (df["EMA_20"] < df["EMA_50"]) & (df["EMA_50"] < df["EMA_200"]) & ~(df["EMA_50_FLAT"]) | (
            df["EMA_200_SLOPE"] < -0.2)
df["Trend"].loc[down[down == True].index] = -1
side = ~(up | down)

df["color"] = df["Trend"].map({1: "green", 0: "black", -1: "red"})

plt.scatter(df.index, df["closeBid"], label="Close", c=df["color"])
plt.plot(df.index, df["EMA_200"], label="EMA(200)")
plt.plot(df.index, df["EMA_20"], label="EMA(20)")
plt.plot(df.index, df["EMA_50"], label="EMA(50)")
plt.legend()
plt.title("5")
plt.show()
