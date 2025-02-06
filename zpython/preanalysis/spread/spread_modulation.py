import joblib
import pandas as pd

from zpython.util.path_util import from_relative_path

kde = joblib.load(from_relative_path("spreadmodelation/gaussian_kde_scipy_gldusd_1.dump"))
df = pd.read_csv(from_relative_path("data-kraken/PAXGUSD_1.csv.zip"), compression="zip")
df["time"] = pd.to_datetime(df["time"])
df.set_index("time", inplace=True)
df = df.rename(columns={"open": "openBid", "high": "highBid", "low": "lowBid", "close": "closeBid"})

spreads = kde.resample(size=len(df))[0]

df["openAsk"] = df["openBid"] + spreads
df["highAsk"] = df["highBid"] + spreads
df["lowAsk"] = df["lowBid"] + spreads
df["closeAsk"] = df["closeBid"] + spreads

df["openAsk"] = round(df["openAsk"], 2)
df["highAsk"] = round(df["highAsk"], 2)
df["lowAsk"] = round(df["lowAsk"], 2)
df["closeAsk"] = round(df["closeAsk"], 2)

df = df[["openBid", "openAsk", "highBid", "highAsk", "lowBid", "lowAsk", "closeBid", "closeAsk", "volume", "trades"]]
df.reset_index(inplace=True)

df.to_csv(from_relative_path("data-kraken-spread/PAXGUSD_1.csv.zip"), compression="zip")
