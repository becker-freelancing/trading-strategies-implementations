import pandas as pd

# Vorher musste hist_data_concat.py ausgeführt werden um BID und ASK in einzelnen gesamtdateien zu haben

path = "C:/Users/jasb/Downloads/"
ask_name = "EURUSD_TICK_ASK.csv.zip"
bid_name = "EURUSD_TICK_BID.csv.zip"
out_name = "EURUSD_TICK_BID_ASK.csv.zip"

ask = pd.read_csv(f"{path}{ask_name}", compression="zip")
bid = pd.read_csv(f"{path}{bid_name}", compression="zip")

ask.columns = ["closeTime", "closeAsk"]
bid.columns = ["closeTime", "closeBid"]

merge = pd.merge(ask, bid, on="closeTime", how="outer")
merge = merge.dropna()
print(merge)

merge.to_csv(f"{path}{out_name}", index=False, compression="zip")
