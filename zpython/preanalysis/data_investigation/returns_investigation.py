import matplotlib

matplotlib.use("TkAgg")
import pandas as pd
from zpython.util import analysis_data
import matplotlib.pyplot as plt
import numpy as np

df: pd.DataFrame = analysis_data(time_frame=1)  # create_indicators(data_read_function=analysis_data)


def max_cumulative_return(x):
    first = x[0]
    max_price = np.max(x)
    diff = max_price - first
    if diff < 0.001:
        return np.nan
    return diff


def min_cumulative_return(x):
    first = x[0]
    max_price = np.min(x)
    diff = max_price - first
    return diff


window = 30
log_returns = df["closeBid"]

max_cum_returns = log_returns.rolling(window=window, min_periods=30).apply(
    max_cumulative_return, raw=True
).shift(-window + 1)

min_cum_returns = log_returns.rolling(window=window, min_periods=30).apply(
    min_cumulative_return, raw=True
).shift(-window + 1)

max_cum_returns = max_cum_returns[max_cum_returns < 50]
min_cum_returns = min_cum_returns[min_cum_returns > -50]

for q in range(0, 100, 10):
    print(f"Quantil = {q}: {round(np.quantile(max_cum_returns, q=(q / 100)), 3)}")

plt.hist(max_cum_returns.dropna().values, bins=50)
plt.title("Max")
plt.show()

plt.hist(min_cum_returns.dropna().values, bins=50)
plt.title("Min")
plt.show()
