import matplotlib

matplotlib.use("TkAgg")
from zpython.util.indicator_creator import create_indicators
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

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

df_res = pd.DataFrame(index=df.index)
df_res.loc[:, "logReturn_closeBid_1min"] = df["logReturn_closeBid_1min"]

atr_scaler = StandardScaler()
atrs = atr_scaler.fit_transform(df[groups["ATR"]])
atr_pca = PCA(n_components=0.8)
atr_pca.fit(atrs)

ema_scaler = StandardScaler()
emas = ema_scaler.fit_transform(df[groups["EMA"]])
ema_pca = PCA(n_components=0.8)
ema_pca.fit(emas)

df['bb_width_20'] = df["BB_Upper_20"] - df["BB_Lower_20"]
df['bb_distance_20'] = df["logReturn_closeBid_1min"] - df["BB_Middle_20"]
bb_scaler = StandardScaler()
bb = bb_scaler.fit_transform(df[["bb_width_20", "bb_distance_20"]])
bb_pca = PCA(n_components=0.8)
bb_pca.fit(bb)

m_scaler = StandardScaler()
ms = m_scaler.fit_transform(df[groups["Momentum"]])
m_pca = PCA(n_components=0.8)
m_pca.fit(ms)

print()
