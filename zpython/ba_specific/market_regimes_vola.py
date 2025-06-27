import matplotlib

matplotlib.use("TkAgg")
from zpython.util.data_split import train_data
import matplotlib.pyplot as plt
from zpython.util import split_on_gaps
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import matplotlib.dates as mdates

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

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(close, label='Closing Price', color='black')

prev_state = None
start_idx = 0

colors = {
    -1: "red",
    1: "green"
}

for i, (time, state) in enumerate(zip(df.index, vola)):
    if state != prev_state and prev_state is not None:
        ax.axvspan(df.index[start_idx], df.index[i],
                   color=colors[prev_state], alpha=0.3)
        start_idx = i
    prev_state = state

# letzten Bereich einzeichnen
ax.axvspan(df.index[start_idx], df.index[-1],
           color=colors[prev_state], alpha=0.3)

labels = {1: "High Volatility", -1: "Low volatility"}
# Legende für Farben
legend_patches = [mpatches.Patch(color=color, label=labels[enum])
                  for enum, color in colors.items()]
ax.legend(handles=legend_patches + [ax.lines[0]], loc='upper left')

formatter = mdates.DateFormatter('%H:%M')
ax.xaxis.set_major_formatter(formatter)
ax.set_title("Volatility Classification")
ax.set_ylabel("ETH/USDC M1")
plt.tight_layout()
plt.show()
