import matplotlib

matplotlib.use("TkAgg")
from zpython.util.data_split import train_data
import matplotlib.pyplot as plt
from zpython.util import split_on_gaps
import pandas_ta as ta
import matplotlib.patches as mpatches
import pandas as pd
import matplotlib.dates as mdates

df = train_data()
df.set_index("closeTime", inplace=True)
df = split_on_gaps(df, 1)[1]
df = df.iloc[:700]
close = df["closeBid"]

print(df.index.min())

ema_50 = ta.ema(close, 50)
ema_100 = ta.ema(close, 100)

trend_slope_shift = 15
trend_reversal_slope_threshold = 0.05
ema_50_slope = (ema_50 - ema_50.shift(trend_slope_shift)) / trend_slope_shift
up = (ema_50 > ema_100) & (ema_50_slope > -trend_reversal_slope_threshold)
down = (ema_50 < ema_100) & (ema_50_slope < trend_reversal_slope_threshold)
trend = pd.Series(0, index=df.index)
trend.loc[up[up == True].index] = 1
trend.loc[down[down == True].index] = -1

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(close, label='Closing Price', color='black')

prev_state = None
start_idx = 0

colors = {
    0: "blue",
    -1: "red",
    1: "green"
}

labels = {
    0: "Sideways Trend",
    1: "Uptrend",
    -1: "Downtrend"
}

for i, (time, state) in enumerate(zip(df.index, trend)):
    if state != prev_state and prev_state is not None:
        ax.axvspan(df.index[start_idx], df.index[i],
                   color=colors[prev_state], alpha=0.3, label=labels[prev_state])
        start_idx = i
    prev_state = state

# letzten Bereich einzeichnen
ax.axvspan(df.index[start_idx], df.index[-1],
           color=colors[prev_state], alpha=0.3, label=labels[prev_state])

ax.plot(ema_50, label="EMA(50)")
ax.plot(ema_100, label="EMA(100)")
# Legende für Farben
legend_patches = [mpatches.Patch(color=color, label=labels[enum])
                  for enum, color in colors.items()]
ax.legend(handles=legend_patches + [ax.lines[0], ax.lines[1], ax.lines[2]], loc='upper left')

formatter = mdates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(formatter)
ax.set_title("Trend Classification")
ax.set_ylabel("ETH/USDC M1")
plt.tight_layout()
plt.show()
