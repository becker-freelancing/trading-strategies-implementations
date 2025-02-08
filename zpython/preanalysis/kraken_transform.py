import os

import pandas as pd

directory = "C:/Users/jasb/AppData/Roaming/krypto-java/data-kraken"

for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path):
        print(file_path)
        df = pd.read_csv(file_path, compression="zip")
        df.columns = ["time", "open", "high", "low", "close", "volume", "trades"]
        if pd.to_datetime(df.iloc[0]["time"]) < pd.Timestamp(year=1990, month=1, day=1):
            df["time"] = pd.to_datetime(df["time"], unit='s')
        else:
            df["time"] = pd.to_datetime(df["time"])
        df = df.rename(
            columns={"time": "closeTime", "open": "openBid", "high": "highBid", "low": "lowBid", "close": "closeBid"})

        file_path = file_path.replace(".zip", "")
        df.to_csv(file_path + ".zip", compression="zip", index=False)
