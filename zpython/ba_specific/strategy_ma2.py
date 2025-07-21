import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pandas as pd

from zpython.util.data_split import validation_data
import pandas_ta as ta
from zpython.ba_specific.candlestick_plot_util import plot_candlesticks

plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20
})

data: pd.DataFrame = validation_data()
data = data.reset_index(drop=True)

start = 1050
end = 1150

ema1 = ta.sma(data.iloc[start - 5:end]["closeBid"], 5).loc[start:end]
ema2 = ta.sma(data.iloc[start - 10:end]["closeBid"], 10).loc[start:end]

shift = 1

down_cross: pd.Series = (ema1 < ema2) & (ema1.shift(shift) > ema2.shift(shift))
up_cross: pd.Series = (ema1 > ema2) & (ema1.shift(shift) < ema2.shift(shift))

fig, ax = plt.subplots()

plot_candlesticks(ax, data.iloc[start:end])

ax.plot(ema1, label="SMA(5)")
ax.plot(ema2, label="SMA(10)")

for idx, value in up_cross.items():
    if value:
        idx_arrow = idx + 1
        low = data.loc[idx_arrow]["lowBid"]
        arrow_start_y = low - 3

        ax.arrow(
            idx_arrow,
            arrow_start_y,
            0,
            abs(low - arrow_start_y) - 1.5,
            head_width=0.9,
            head_length=1,
            fc='blue',
            ec='blue'
        )

for idx, value in down_cross.items():
    if value:
        idx_arrow = idx + 1
        high = data.loc[idx_arrow]["highBid"]
        arrow_start_y = high + 3

        ax.arrow(
            idx_arrow,
            arrow_start_y,
            0,
            (abs(high - arrow_start_y) - 1.5) * -1,
            head_width=0.9,
            head_length=1,
            fc='red',
            ec='red'
        )

plt.tick_params(axis='x', bottom=False, top=False, which="both", labelbottom=False)
plt.xlabel("Time")
plt.ylabel("Price")
plt.title("Dual Simple Moving Average Strategy Example")
plt.legend()
plt.show()
