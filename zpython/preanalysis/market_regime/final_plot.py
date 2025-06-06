import matplotlib

matplotlib.use("TkAgg")
from zpython.util import analysis_data, split_on_gaps
from zpython.util.market_regime import MarketRegimeDetector, market_state_colors
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

df = analysis_data()
det = MarketRegimeDetector()
det.fit(df)
split = split_on_gaps(df, 1)
df = split[1]
trans = det.transform(df)

fig, ax = plt.subplots(figsize=(10, 5))

# Plot der Daten
ax.plot(df["closeTime"], df['closeBid'], label='Close', color='black')

# Hintergrundfärbung pro Abschnitt
prev_state = None
start_idx = 0

for i, (time, state) in enumerate(zip(df["closeTime"], trans)):
    if state != prev_state and prev_state is not None:
        ax.axvspan(df["closeTime"].loc[df.index[start_idx]], df["closeTime"].loc[df.index[i]],
                   color=market_state_colors()[prev_state], alpha=0.3)
        start_idx = i
    prev_state = state

# letzten Bereich einzeichnen
ax.axvspan(df["closeTime"].loc[df.index[start_idx]], df["closeTime"].loc[df.index[-1]],
           color=market_state_colors()[prev_state], alpha=0.3)

# Legende für Farben
legend_patches = [mpatches.Patch(color=color, label=enum)
                  for enum, color in market_state_colors().items()]
ax.legend(handles=legend_patches + [ax.lines[0]], loc='upper left')

plt.tight_layout()
plt.show()
