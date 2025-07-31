import matplotlib
import pandas as pd

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20
})

c2 = [20, 55, 90, -1, -3, 37, 87, 79, 85, -25, -7, -34, 95, -24, 59, 38, -32, -29, -64, 72, -100, 64, 4, -38, 14, -28,
      -1, 43, -17, 49, -14, -9, 40, 0, 68, 6, -50, 95, 39, 90, 66, -53, -48, -54, 52, -49, 74, 21, 71, 17, -500, 56, 89,
      -20, 90, -27, 44, 14, 61, 9, 13, -57, 75, 10, -25, 52, 61, 45, 20, -34, -400, 66, -34, 47, -30, 46, 11, 94, 0,
      -70, 0, 58, -28, 33, 13, -50, 85, 25, -42, -33, 52, -14, 81, 85, -65, 21, 97, 96, 40, 73]
c1 = [-35, -18, -27, 96, -24, -45, 58, 50, -30, 13, 92, 7, -41, -15, 32, 61, 3, 98, -24, 3, -36, 20, 36, 1, 81, -9, -34,
      81, 78, 8, -47, -47, 52, 32, 24, 53, 27, -7, 34, 92, 96, 34, 11, -36, -20, 28, -31, 68, 47, 61, 3, 28, -29, 76, 1,
      68, 74, -50, -6, 69, -16, -5, -13, -45, -2, 81, -15, 62, 80, 22, -34, -29, -32, 1, -14, -22, 67, 97, 73, 66, 83,
      50, 33, 3, 22, -13, 31, 0, 91, 12, 83, -22, 62, -47, 84, 79, 66, 71, -45, -41]


def render(df: pd.DataFrame, ax1):
    df["cum"] = df["pnl"].cumsum() + 5000
    df["rolMax"] = df["cum"].cummax()
    df["drawdown"] = df["cum"] / df["rolMax"] - 1
    df[df["drawdown"] > 0] = 0
    ax1.plot(df["time"], df["cum"], label="Equity", color="blue")
    ax1.set_ylabel('Account Equity', color='blue')
    ax1.set_xlabel("Trade Index")
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.fill_between(df['time'], df['drawdown'] * 100, color='red', alpha=0.3, label='Drawdown')
    ax2.set_ylabel('Drawdown (%)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(-20, 0)

    # Legende kombinieren
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='lower right')


fig, axs = plt.subplots(1, 2, figsize=(16, 9))

df1 = pd.DataFrame(data={"pnl": c1, "time": list(range(len(c1)))})
render(df1, axs[0])
axs[0].set_title("Preferred Equity Curve")

df2 = pd.DataFrame(data={"pnl": c2, "time": list(range(len(c1)))})
render(df2, axs[1])
axs[1].set_title("Volatile Equity Curve")

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.suptitle("Maximum Drawdown Comparison")
plt.show()
