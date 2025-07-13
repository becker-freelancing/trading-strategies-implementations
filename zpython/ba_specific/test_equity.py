import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Dummy-Daten erzeugen
np.random.seed(0)
dates = pd.date_range(start="2020-01-01", periods=200)
returns = np.random.normal(0.0005, 0.01, size=200)
strategy_value = 100 * (1 + pd.Series(returns)).cumprod()

# DataFrame & Drawdown berechnen
df = pd.DataFrame({'Date': dates, 'Strategy_Value': strategy_value})
df['Rolling_Max'] = df['Strategy_Value'].cummax()
df['Drawdown'] = df['Strategy_Value'] / df['Rolling_Max'] - 1  # in Dezimalform

# Plot mit zwei Y-Achsen
fig, ax1 = plt.subplots(figsize=(12, 6))

# Linke Achse: Equity Curve
ax1.plot(df['Date'], df['Strategy_Value'], label='Equity Curve', color='blue')
ax1.set_ylabel('Portfolio-Wert', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_title("Equity Curve mit gefülltem Drawdown")
ax1.grid(True)

# Rechte Achse: Drawdown (als Fläche)
ax2 = ax1.twinx()
ax2.fill_between(df['Date'], df['Drawdown'] * 100, color='red', alpha=0.3, label='Drawdown')
ax2.set_ylabel('Drawdown (%)', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Legende kombinieren
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

plt.tight_layout()
plt.show()
