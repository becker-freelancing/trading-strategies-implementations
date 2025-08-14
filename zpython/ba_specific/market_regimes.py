import matplotlib

matplotlib.use("TkAgg")
from zpython.util.data_split import train_data
import matplotlib.pyplot as plt
from zpython.util import split_on_gaps
import pandas_ta as ta
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import matplotlib.dates as mdates

plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20
})
df = train_data()
df.set_index("closeTime", inplace=True)
df = split_on_gaps(df, 1)[1]
df = df.iloc[:700]
close = df["closeBid"]

# vola_split_thresholds = 0.0005497362448184632

returns = np.log(close / close.shift(1))
volas = returns.rolling(window=30).std()
vola_split_thresholds = volas.quantile(0.5)

returns = np.log(close / close.shift(1))
vola = returns.rolling(window=30).std() + 0.00015

low = vola <= vola_split_thresholds
vola = pd.Series(1, index=close.index)
vola.loc[low[low == True].index] = -1

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

mr = pd.Series(0, index=df.index)
downLowVola = (trend == -1) & (vola == 1)
mr.loc[downLowVola[downLowVola == True].index] = 1

sideHighvola = (trend == 0) & (vola == 1)
mr.loc[sideHighvola[sideHighvola == True].index] = 2

sideLowVola = (trend == 0) & (vola == -1)
mr.loc[sideLowVola[sideLowVola == True].index] = 3

upHighVola = (trend == 1) & (vola == 1)
mr.loc[upHighVola[upHighVola == True].index] = 4

upLowVola = (trend == 1) & (vola == -1)
mr.loc[upLowVola[upLowVola == True].index] = 5

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(close, label='Closing Price', color='black')

prev_state = None
start_idx = 0

colors = {
    0: "red",
    1: "#FFCCCC",
    2: "blue",
    3: "lightblue",
    4: "green",
    5: "lightgreen"
}

for i, (time, state) in enumerate(zip(df.index, mr)):
    if state != prev_state and prev_state is not None:
        ax.axvspan(df.index[start_idx], df.index[i],
                   color=colors[prev_state], alpha=0.3)
        start_idx = i
    prev_state = state

# letzten Bereich einzeichnen
ax.axvspan(df.index[start_idx], df.index[-1],
           color=colors[prev_state], alpha=0.3)

labels = {
    0: "Downtrend + High Volatility",
    1: "Downtrend + Low Volatility",
    2: "Sideways Trend + High Volatility",
    3: "Sideways Trend + Low Volatility",
    4: "Uptrend + High Volatility",
    5: "Uptrend + Low Volatility"
}
# Legende für Farben
legend_patches = [mpatches.Patch(color=color, label=labels[enum])
                  for enum, color in colors.items()]
ax.legend(handles=legend_patches + [ax.lines[0]], loc='upper right')

formatter = mdates.DateFormatter('%I %p')
ax.xaxis.set_major_formatter(formatter)
ax.set_title("Market Regime Classification")
ax.set_ylabel("ETH/USDC M1")
plt.tight_layout()
plt.show()
