import numpy as np
import pandas as pd

from zpython.models.regression.data_preparation import read_data
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair
from zpython.util.path_util import from_relative_path

data_source = DataSource.HIST_DATA
pair = Pair.EURUSD_5
stop = 10  # 0.0001
limit = 30
size = 1

stop_distance = stop / 100_000 / size
limit_distance = limit / 100_000 / size

# Ziel: Drei Outputs -> Kaufen, Verkaufen, Nichts tun (Jeweils 0, 1)

# Indexes hinzufügen, wann Buy_limit, Buy_Stop, Sell_Limit, Sell_Stop

# schauen, ob buy und sell valid sind -> Ist buy/sell limit vor stop?

# Entscheiden, ob Buy oder Sell
# -> Falls nur eins existiert, dann das nehmen
# -> Falls beides existiert, dann das nehmen, wo vorher limit erreicht wurde
# -> Falls keins existiert, dann None

df = read_data(data_source.file_path(pair))
df.reset_index(inplace=True, names="closeTime")
df = df[df["closeTime"] >= pd.Timestamp(year=2015, month=1, day=1)]
df = df.reset_index(drop=True)


# df["BuyLimitReached"] = df.index.map(
#     lambda i: np.sum(df.loc[i+1:, 'closeBid'] >= df.loc[i, 'closeBid'] + limit_distance)
# )

def add_threshold_index_gt(threshold, target_column):
    werte = df['closeBid'].values
    result = np.full(len(werte), np.nan)  # initialisieren mit NaN für keine Steigerung

    # Durch alle Zeilen iterieren
    for i in range(len(werte)):
        # Wenn noch nachfolgende Werte existieren
        if i + 1 < len(werte):
            # Finde den ersten Index der nachfolgenden Werte, bei denen der Wert mindestens um threshold steigt
            condition = werte[i + 1:] >= werte[i] + threshold
            idx = np.argmax(condition) if np.any(condition) and condition[np.argmax(condition)] else np.nan

            if not np.isnan(idx):  # Wenn ein Treffer gefunden wurde
                result[i] = i + 1 + idx  # den tatsächlichen Index zuweisen
            else:
                result[i] = np.nan  # Wenn kein Treffer gefunden wurde, NaN setzen
        else:
            result[i] = np.nan  # Wenn keine nachfolgenden Werte existieren, NaN setzen

    df[target_column] = result


def add_threshold_index_lt(threshold, target_column):
    werte = df['closeBid'].values
    result = np.full(len(werte), np.nan)  # initialisieren mit NaN für keine Steigerung

    # Durch alle Zeilen iterieren
    for i in range(len(werte)):
        # Wenn noch nachfolgende Werte existieren
        if i + 1 < len(werte):
            # Finde den ersten Index der nachfolgenden Werte, bei denen der Wert mindestens um threshold steigt
            condition = werte[i + 1:] <= werte[i] + threshold
            idx = np.argmax(condition) if np.any(condition) and condition[np.argmax(condition)] else np.nan

            if not np.isnan(idx):  # Wenn ein Treffer gefunden wurde
                result[i] = i + 1 + idx  # den tatsächlichen Index zuweisen
            else:
                result[i] = np.nan  # Wenn kein Treffer gefunden wurde, NaN setzen
        else:
            result[i] = np.nan  # Wenn keine nachfolgenden Werte existieren, NaN setzen

    df[target_column] = result


add_threshold_index_gt(limit_distance, "BuyLimitIdx")
add_threshold_index_lt(-stop_distance, "BuyStopIdx")
add_threshold_index_lt(-limit_distance, "SellLimitIdx"),
add_threshold_index_gt(stop_distance, "SellStopIdx")

df["BuyValid"] = np.where(df['BuyLimitIdx'].isna(), 0,
                          np.where(df["BuyStopIdx"].isna(), 1, np.where(df['BuyStopIdx'] < df['BuyLimitIdx'], 0, 1)))
df["SellValid"] = np.where(df['SellLimitIdx'].isna(), 0, np.where(df["SellStopIdx"].isna(), 1,
                                                                  np.where(df['SellStopIdx'] < df['SellLimitIdx'], 0,
                                                                           1)))

df["SellOutput"] = np.where(df["SellValid"] == 0, 0,
                            np.where(df["BuyValid"] == 0, 1, np.where(df["BuyLimitIdx"] < df["SellLimitIdx"], 0, 1)))
df["BuyOutput"] = np.where(df["BuyValid"] == 0, 0,
                           np.where(df["SellValid"] == 0, 1, np.where(df["BuyLimitIdx"] < df["SellLimitIdx"], 1, 0)))
df["NoneOutput"] = np.where(((df["SellOutput"] == 0) & (df["BuyOutput"] == 0)), 1, 0)

df_trans = df.drop(columns=["BuyValid", "SellValid", "BuyLimitIdx", "BuyStopIdx", "SellLimitIdx", "SellStopIdx"])

write_path = from_relative_path(
    f"training-data/classification/{data_source.value}_{pair.name()}limit_{limit}_stop_{stop}.csv.zip")
df_trans.to_csv(write_path, index=False, compression="zip")
