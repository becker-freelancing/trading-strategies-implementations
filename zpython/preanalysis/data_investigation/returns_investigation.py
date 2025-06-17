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


def greater_take_take_order(x):
    first = x[0]
    greater = np.where(x > first * 1.001100605)[0]
    return np.any(greater)


def less_take_take_order(x):
    first = x[0]
    greater = np.where(x < first * (1 / 1.001100605))[0]
    return np.any(greater)


def min_cumulative_return(x):
    first = x[0]
    max_price = np.min(x)
    diff = max_price - first
    return diff


window = 100
log_returns = df["closeBid"]

max_cum_returns = log_returns.rolling(window=window, min_periods=window).apply(
    max_cumulative_return, raw=True
).shift(-window + 1)

greater_take_take = log_returns.rolling(window=window, min_periods=window).apply(
    greater_take_take_order, raw=True
).shift(-window + 1)

less_take_take = log_returns.rolling(window=window, min_periods=window).apply(
    less_take_take_order, raw=True
).shift(-window + 1)

min_cum_returns = log_returns.rolling(window=window, min_periods=window).apply(
    min_cumulative_return, raw=True
).shift(-window + 1)

max_cum_returns = max_cum_returns[max_cum_returns < 50]
min_cum_returns = min_cum_returns[min_cum_returns > -50]

print("Max Quantiles:")
for q in range(0, 100, 10):
    print(f"Quantil = {q}: {round(np.quantile(max_cum_returns, q=(q / 100)), 3)}")

print("\n\n\nMin Quantiles:")
for q in range(0, 100, 10):
    print(f"Quantil = {q}: {round(np.quantile(np.abs(min_cum_returns), q=(q / 100)), 3)}")

print(f"\n\n\nGreater Take Take: {np.count_nonzero(greater_take_take) / len(greater_take_take) * 100}%")
print(f"Less Take Take: {np.count_nonzero(less_take_take) / len(less_take_take) * 100}%")

plt.hist(log_returns)
plt.title("Price")
plt.show()

plt.hist(max_cum_returns.dropna().values, bins=50)
plt.title("Max")
plt.show()

plt.hist(min_cum_returns.dropna().values, bins=50)
plt.title("Min")
plt.show()
