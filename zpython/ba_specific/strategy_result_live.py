import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")
import pandas as pd

plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20
})

best_cum = pd.DataFrame(data={
    "pnl": [-66.8500287, -73.06180848, -46.03045442, -65.80755477, -47.82438395, -93.53868726, -35.8574317,
            -47.19254239, -24.33727407, -71.71996997, -62.96361664, -61.28651438, -49.196488, -49.3646036, -97.291383,
            26.13835379, -25.52593787, 212.89637633, -47.76800042, -228.69505507, -24.08325671, -0.84995708,
            13.52630425, -4.58280388, 11.25970052, 13.265491, 75.31780535, -48.97159838, -36.28817183, -22.73707259,
            -24.47082789, -34.15357348, -64.25506937, -55.83685594, 36.87838098, 8.60173558, 131.020512, -29.36809065,
            53.91527019, -10.34266305, -107.04344227, -45.34532098, -52.71087939, -49.84960974, -43.5238215,
            -60.67175482, -15.5775392, -16.9893127, 304.02894192, 71.66417996, 289.96239174, 101.28238392, 25.48487615,
            20.87369482, 48.0044325, -62.67807124, -65.97536205, -91.0656848, 32.7834088, -48.45337664, -66.65474373,
            -56.90158209, -54.63224977, -51.58987732, -66.55582206, -57.39539513]
})

fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(16, 9))


def render(df: pd.DataFrame, ax1):
    df["cum"] = df["pnl"].cumsum() + 5000
    df["rolMax"] = df["cum"].cummax()
    df["drawdown"] = df["cum"] / df["rolMax"] - 1
    ax1.plot(df.index, df["cum"], label="Equity", color="blue")
    ax1.set_ylabel('Account Equity', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True)
    ax1.set_xlabel("Trade Index")

    ax2 = ax1.twinx()
    ax2.fill_between(df.index, df['drawdown'] * 100, color='red', alpha=0.3, label='Drawdown')
    ax2.set_ylabel('Drawdown (%)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    # Legende kombinieren
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='lower right')


render(best_cum, axs)

plt.title("Triple Exponential Moving Average Strategy Live Results")
plt.tight_layout()
plt.show()
