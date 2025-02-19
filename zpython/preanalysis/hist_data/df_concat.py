import pandas as pd

df1 = pd.read_csv("C:/Users/jasb/Downloads/EURUSD_TICK_BID.csv.zip", compression="zip")
df2 = pd.read_csv("C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_TICK_BID.csv.zip", compression="zip")

df1["closeTime"] = pd.to_datetime(df1["closeTime"])
df2["closeTime"] = pd.to_datetime(df2["closeTime"])

concat = pd.concat([df1, df2])

concat = concat.sort_values("closeTime")

concat.to_csv("C:/Users/jasb/Downloads/EURUSD_TICK_BID.csv.zip", compression="zip", index=False)
