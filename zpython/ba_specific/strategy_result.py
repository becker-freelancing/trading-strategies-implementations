import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")
import pandas as pd
import os
from zpython.util.path_util import from_relative_path
import matplotlib.dates as mdates

base_path = from_relative_path("results")


def strategy():
    paths = os.listdir(base_path)
    for i, p in zip(range(len(paths)), paths):
        print(f"{i} - {p}")

    i = int(input("Strategy"))
    return paths[i]


def execution():
    strat = strategy()
    base = from_relative_path(f"results/{strat}")
    paths = [p for p in os.listdir(base) if p.endswith(".csv.zst")]
    for i, p in zip(range(len(paths)), paths):
        print(f"{i} - {p}")

    i = int(input("Execution"))
    return base, paths[i].replace(".csv.zst", ".json")


base, stratexec = execution()

best_cum = pd.read_json(f"{base}/PY_BEST_CUM_{stratexec}")
best_max = pd.read_json(f"{base}/PY_BEST_MAX_{stratexec}")
best_min = pd.read_json(f"{base}/PY_BEST_MIN_{stratexec}")
most_trades = pd.read_json(f"{base}/PY_MOST_TRADES_{stratexec}")

fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(16, 9))


def render(df: pd.DataFrame, col, row):
    df["cum"] = df["pnl"].cumsum() + 5000
    df["rolMax"] = df["cum"].cummax()
    df["drawdown"] = df["cum"] / df["rolMax"] - 1
    ax1 = axs[row, col]
    ax1.plot(df["time"], df["cum"], label="Equity", color="blue")
    ax1.set_ylabel('Account Equity', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.fill_between(df['time'], df['drawdown'] * 100, color='red', alpha=0.3, label='Drawdown')
    ax2.set_ylabel('Drawdown (%)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    # Legende kombinieren
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
    ax1.xaxis.set_major_locator(mdates.MonthLocator())  # jeden Monat
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m'))


render(best_cum, 0, 0)
render(best_max, 1, 0)
render(best_min, 0, 1)
render(most_trades, 1, 1)

plt.tight_layout()
plt.show()
