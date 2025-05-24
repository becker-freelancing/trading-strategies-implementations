import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from zpython.util import train_data
import numpy as np
import warnings
from zpython.util import split_on_gaps

warnings.filterwarnings('ignore')

print("Read data")
df = train_data()
print("Create indicators")
dfs = split_on_gaps(df, 1)
for df in [dfs[2]]:
    df = df.reset_index(drop=True)

    df["Return"] = np.log(df["closeBid"] / df["closeBid"].shift(1))
    df["volatility"] = df["Return"].rolling(window=30).std()

    high_thres = df["volatility"].quantile(0.5)

    high = df["volatility"] > high_thres
    low = df["volatility"] < high_thres
    df["vol_class"] = 0
    df["vol_class"].loc[high[high == True].index] = 1
    df["vol_class"].loc[low[low == True].index] = -1

    df = df.dropna()
    df["color"] = df["vol_class"].map({1: "green", 0: "black", -1: "red"})

    plt.scatter(df.index, df["closeBid"], label="Close", c=df["color"])
    plt.legend()
    plt.show()
