import pandas as pd

pair = "BTCUSDT"
spread = 0.01  # Außer bei ETHBTC, dann 0.00001, sonst 0.01
digits = 2

df = pd.read_csv(f"./{pair}_1_raw.csv")

df["openBid"] = df["open"]
df["openAsk"] = round(df["openBid"] + spread, digits)
df["highBid"] = df["high"]
df["highAsk"] = round(df["highBid"] + spread, digits)
df["lowBid"] = df["low"]
df["lowAsk"] = round(df["lowBid"] + spread, digits)
df["closeBid"] = df["close"]
df["closeAsk"] = round(df["closeBid"] + spread, digits)
df["closeTime"] = df["close_time"]
df["quoteAssetVolume"] = df["quote_asset_volume"]
df["numberOfTrades"] = df["number_of_trades"]
df["takerBuyBase"] = df["taker_buy_base"]
df["takerBuyQuote"] = df["taker_buy_quote"]

df = df[["closeTime", "openBid", "openAsk", "highBid", "highAsk", "lowBid", "lowAsk", "closeBid", "closeAsk", "volume",
         "quoteAssetVolume", "numberOfTrades", "takerBuyBase", "takerBuyQuote"]]
df["closeTime"] = pd.to_datetime(df["closeTime"], format="mixed")

df.drop_duplicates(subset=['closeTime'], keep='first', inplace=True)

df = df.sort_values("closeTime")

df["closeTime"] = df["closeTime"].apply(lambda t: t.floor("s") + pd.Timedelta(seconds=1))

df.to_csv(f"./{pair}_1.csv.zip", index=False, compression="zip")
