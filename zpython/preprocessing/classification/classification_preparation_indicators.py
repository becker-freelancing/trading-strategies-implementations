import pandas as pd
import pandas_ta as ta

from zpython.util.data_source import DataSource
from zpython.util.pair import Pair
from zpython.util.path_util import from_relative_path

data_source = DataSource.HIST_DATA
pair = Pair.EURUSD_5
reindex_freq = "5min"
stop = 10
limit = 30

write_path = from_relative_path(
    f"training-data/classification/{data_source.value}_{pair.name()}_limit_{limit}_stop_{stop}.csv.zip")

df = pd.read_csv(write_path, compression="zip")
df["closeTime"] = pd.to_datetime(df["closeTime"])

df["ema_5"] = ta.ema(df["closeBid"], length=5)
df["ema_10"] = ta.ema(df["closeBid"], length=10)
df["ema_20"] = ta.ema(df["closeBid"], length=20)
df["ema_50"] = ta.ema(df["closeBid"], length=50)
df["ema_200"] = ta.ema(df["closeBid"], length=200)
df["ema_20_close_diff"] = df["closeBid"] - df["ema_20"]
df["ema_20_close_ratio"] = df["closeBid"] / df["ema_20"]

df["rsi_7"] = ta.rsi(df["closeBid"], length=7)
df["rsi_14"] = ta.rsi(df["closeBid"], length=14)
df["rsi_7_scaled"] = df["rsi_7"] / 100
df["rsi_14_scaled"] = df["rsi_14"] / 100

stoch_14_3 = ta.stoch(df["highBid"], df["lowBid"], df["closeBid"], k=14, d=3)
df["stoch_14_3_k"], df["stoch_14_3_d"] = stoch_14_3["STOCHk_14_3_3"], stoch_14_3["STOCHd_14_3_3"]
stoch_5_3 = ta.stoch(df["highBid"], df["lowBid"], df["closeBid"], k=5, d=3)
df["stoch_5_3_k"], df["stoch_5_3_d"] = stoch_5_3["STOCHk_5_3_3"], stoch_5_3["STOCHd_5_3_3"]

df["stoch_k_d_diff_14_3"] = df["stoch_14_3_k"] - df["stoch_14_3_d"]

df["atr_14"] = ta.atr(df["highBid"], df["lowBid"], df["closeBid"], length=14)
df["atr_14_close_ratio"] = df["atr_14"] / df["closeBid"]

bbands = ta.bbands(df["closeBid"], length=20, std=2)
df["bb_20_2_lower"], df["bb_20_2_high"], df["bb_20_2_mid"] = bbands["BBL_20_2.0"], bbands["BBU_20_2.0"], bbands[
    "BBM_20_2.0"]

df = df.round(5)

df.to_csv(write_path, index=False, compression="zip")
