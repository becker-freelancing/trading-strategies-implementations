import os
import zipfile

import pandas as pd

path = "C:/Users/jasb/Downloads/histdatabid"
write_name = "EURUSD_TICK_BID.csv.zip"

for filename in os.listdir(path):
    file_path = os.path.join(path, filename)
    if os.path.isfile(file_path) and ".zip" in file_path:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(path)

df = pd.DataFrame()

for filename in os.listdir(path):
    file_path = os.path.join(path, filename)
    if os.path.isfile(file_path) and ".csv" in file_path:
        csv = pd.read_csv(file_path, header=None, delimiter=";")
        df = pd.concat([df, csv])

df.columns = ["closeTime", "closeBid", "volume"]
df = df.drop(columns=["volume"])
df["closeTime"] = pd.to_datetime(df["closeTime"], format='%Y%m%d %H%M%S')
df = df.sort_values("closeTime")
# df.set_index("closeTime", inplace=True)
df.drop_duplicates(subset="closeTime")
print(len(df))
df.to_csv(f"{path}/{write_name}", compression="zip", index=False)
