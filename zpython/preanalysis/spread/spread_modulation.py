import joblib
import pandas as pd

from zpython.util.path_util import from_relative_path

kde = joblib.load(from_relative_path("spreadmodelation/gaussian_kde_scipy_eurusd_1_hist_data.dump"))
path = from_relative_path("data-histdata/EURUSD_1.csv.zip")
df = pd.read_csv(path, compression="zip")
df["closeTime"] = pd.to_datetime(df["closeTime"])
df.set_index("closeTime", inplace=True)
# df = df.rename(columns={"open": "openBid", "high": "highBid", "low": "lowBid", "close": "closeBid"})

spreads = kde.resample(size=len(df))[0]

df["openAsk"] = df["openBid"] + spreads
df["highAsk"] = df["highBid"] + spreads
df["lowAsk"] = df["lowBid"] + spreads
df["closeAsk"] = df["closeBid"] + spreads

df["openAsk"] = round(df["openAsk"], 5)
df["highAsk"] = round(df["highAsk"], 5)
df["lowAsk"] = round(df["lowAsk"], 5)
df["closeAsk"] = round(df["closeAsk"], 5)

df = df[["openBid", "openAsk", "highBid", "highAsk", "lowBid", "lowAsk", "closeBid", "closeAsk"]]
df.reset_index(inplace=True)

df.to_csv(path, compression="zip", index=False)
