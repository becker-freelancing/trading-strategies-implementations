# matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from zpython.util.data_split import train_data

df: pd.DataFrame = train_data().iloc[-100000:]


def max_pos_change(x):
    x = x.values
    start = x[0]
    m = np.max(x)
    return (m / start) - 1


def min_pos_change(x):
    x = x.values
    start = x[0]
    m = np.min(x)
    return (m / start) - 1


def prune(x):
    x = x.dropna().values
    x = np.abs(x)
    q = np.quantile(x, 0.6)
    return x[np.where(x < q)[0]]


for window in [240]:
    max_change = df["closeBid"].rolling(window, min_periods=window).apply(max_pos_change)
    max_change = prune(max_change)
    min_change = df["closeBid"].rolling(window, min_periods=window).apply(min_pos_change)
    min_change = prune(min_change)

    plt.hist(max_change, label="Max. Change", alpha=0.2)
    plt.hist(min_change, label="Min. Change", alpha=0.2)
    plt.title(f"Window = {window} min")
    plt.legend()
    plt.show()
