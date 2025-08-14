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

data = validation_data()
data = data.reset_index(drop=True)

start = 1050
end = 1150

ema1 = ta.ema(data.iloc[start - 5:end]["closeBid"], 5).loc[start:end]
ema2 = ta.ema(data.iloc[start - 10:end]["closeBid"], 10).loc[start:end]
ema3 = ta.ema(data.iloc[start - 30:end]["closeBid"], 20)
shift = 1

down_cross: pd.Series = (ema1 < ema2) & (ema1.shift(shift) > ema2.shift(shift))
up_cross: pd.Series = (ema1 > ema2) & (ema1.shift(shift) < ema2.shift(shift))

ema3_slope = (ema3 - ema3.shift(10)) / 10
thres = 0.15
s = (ema3_slope > thres) | (ema3_slope < -thres)

fig, ax = plt.subplots()
plot_candlesticks(ax, data.iloc[start:end])

ax.plot(ema1, label="EMA(5)")
ax.plot(ema2, label="EMA(10)")
ax.plot(ema3.loc[start:end], label="EMA(20)")

for idx, value in up_cross.items():
    if value:
        idx_arrow = idx
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
        idx_arrow = idx
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
current_value = s.iloc[30]
start_idx = s.index[30]
for i in range(30, len(s)):
    if s.iloc[i] != current_value:
        end_idx = s.index[i]
        ax.axvspan(start_idx, end_idx, color='green' if current_value else 'red', alpha=0.3)
        current_value = s.iloc[i]
        start_idx = end_idx

# Letzten Bereich einfügen
ax.axvspan(start_idx, s.index[-1] + 1, color='green' if current_value else 'red', alpha=0.3)
plt.tick_params(axis='x', bottom=False, top=False, which="both", labelbottom=False)
plt.xlabel("Time")
plt.ylabel("Price")
plt.title("Triple Exponential Moving Average Strategy Example")
plt.legend()
plt.show()
