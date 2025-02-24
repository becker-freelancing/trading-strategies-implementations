import pandas as pd

from zpython.preprocessing.classification.classification_preparation_2 import read_data_for_preparation, add_outputs
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair

errors = pd.read_csv("backtest_results.csv")

df = read_data_for_preparation(DataSource.HIST_DATA, Pair.EURUSD_1_2024, 3000)

for idx, row in errors.iterrows():
    stop, limit, size = row["stop"], row["limit"], row["size"]
    df_2 = add_outputs(df, stop, limit, size)
    total_len = len(df_2)
    buy_len = len(df_2[df_2["BuyOutput"] == 1])
    sell_len = len(df_2[df_2["SellOutput"] == 1])
    none_len = len(df_2[df_2["NoneOutput"] == 1])

    errors.loc[idx, "ExpectedBuyOutputRatio"] = (buy_len / total_len)
    errors.loc[idx, "ExpectedSellOutputRatio"] = (sell_len / total_len)
    errors.loc[idx, "ExpectedNoneOutputRatio"] = (none_len / total_len)

errors.to_csv("./new_errors.csv", index=False)
