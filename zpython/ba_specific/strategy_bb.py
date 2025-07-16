import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

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

l = 5
s = 1.4
pref = f"_{l}_{s}"
bb = ta.bbands(data.iloc[start - 5:end]["closeBid"], l, s).loc[start:end]

low = bb[f"BBL{pref}"]
mid = bb[f"BBM{pref}"]
up = bb[f"BBU{pref}"]

close = data["closeBid"].iloc[start:end]
open = data["openBid"].iloc[start:end]

up_cross = (open < low) & (close > low) & (close < mid)
down_cross = (open > up) & (close < up) & (close > mid)

fig, ax = plt.subplots()
plot_candlesticks(ax, data.iloc[start:end])

ax.plot(low, color="tab:blue")
ax.plot(mid)
ax.plot(up, color="tab:blue")

ax.fill_between(mid.index, low, up, alpha=0.1)

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

plt.tick_params(axis='x', bottom=False, top=False, which="both", labelbottom=False)
plt.xlabel("Time")
plt.ylabel("Price")
plt.title("Bollinger Bands Strategy Example")
plt.show()
