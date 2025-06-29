import matplotlib

matplotlib.use("TkAgg")
from zpython.util.indicator_creator import create_indicators
import matplotlib.pyplot as plt
import pandas as pd

df = create_indicators()[0].iloc[-10000:]
groups = {
    "ATR": ["ATR_14", "ATR_5", "ATR_7", "ATR_10", "ATR_18", ],
    "EMA": ["EMA_20", "EMA_10", "EMA_5", "EMA_30", "EMA_50", "EMA_200", ],
    "RSI": ["RSI_14", "RSI_7", "RSI_20", ],
    "MACD": ["MACD_12_26_9", "MACD_Signal_12_26_9", ],
    "Bollinger Bands": ["BB_Upper_20", "BB_Middle_20", "BB_Lower_20", "BB_Upper_15", "BB_Middle_15", "BB_Lower_15",
                        "BB_Upper_25", "BB_Middle_25", "BB_Lower_25", ],
    "Momentum": ["momentum_2", "momentum_3", "momentum_6", "momentum_9", "momentum_12", ],
    "Returns": ["logReturn_lowBid_1min", "logReturn_lowBid_2min", "logReturn_lowBid_3min", "logReturn_lowBid_6min",
                "logReturn_lowBid_9min", "logReturn_lowBid_12min", "logReturn_closeBid_1min", "logReturn_closeBid_2min",
                "logReturn_closeBid_3min", "logReturn_closeBid_6min", "logReturn_closeBid_9min",
                "logReturn_closeBid_12min", "logReturn_highBid_1min", "logReturn_highBid_2min",
                "logReturn_highBid_3min", "logReturn_highBid_6min", "logReturn_highBid_9min",
                "logReturn_highBid_12min", ]
}

df["lr_+1min"] = df["logReturn_closeBid_1min"].shift(-1)
df["lr_+2min"] = df["logReturn_closeBid_2min"].shift(-2)
df["lr_+3min"] = df["logReturn_closeBid_3min"].shift(-3)
df["lr_+6min"] = df["logReturn_closeBid_6min"].shift(-6)
df["lr_+9min"] = df["logReturn_closeBid_9min"].shift(-9)
df["lr_+12min"] = df["logReturn_closeBid_12min"].shift(-12)
df = df.dropna()
target = ["lr_+1min",
          "lr_+2min",
          "lr_+3min",
          "lr_+6min",
          "lr_+9min",
          "lr_+12min"]

for group_name, group_content in groups.items():
    corr_df = df[group_content + target]
    corr_matrix = corr_df.corr()
    # matplotlib_corr_matrix()
    pd.plotting.scatter_matrix(corr_df, alpha=0.2)
    plt.show()


def matplotlib_corr_matrix():
    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.matshow(corr_matrix, cmap='coolwarm')
    # Farblegende hinzufügen
    fig.colorbar(cax)
    # Achsen beschriften
    ax.set_xticks(range(len(corr_matrix.columns)))
    ax.set_yticks(range(len(corr_matrix.columns)))
    ax.set_xticklabels(corr_matrix.columns)
    ax.set_yticklabels(corr_matrix.columns)
    # Achsenbeschriftung rotieren
    plt.xticks(rotation=45)
    # Titel hinzufügen (optional)
    plt.title('Korrelationsmatrix', pad=20)
    # Plot anzeigen
    plt.tight_layout()
    plt.show()
