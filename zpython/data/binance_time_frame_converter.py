import pandas as pd

pair = "ETHEUR"

input = pd.read_csv(f"./{pair}_1.csv")
input["closeTime"] = pd.to_datetime(input["closeTime"])
input.set_index("closeTime", inplace=True)


def for_tf(tf_min):
    write_path = f"./{pair}_{tf_min}.csv.zip"
    in_re = input.resample(f'{tf_min}min').agg({
        "openBid": "first",
        "openAsk": "first",
        "highBid": "max",
        "highAsk": "max",
        "lowBid": "min",
        "lowAsk": "min",
        "closeBid": "last",
        "closeAsk": "last",
        "volume": "sum",
        "quoteAssetVolume": "sum",
        "numberOfTrades": "sum",
        "takerBuyBase": "sum",
        "takerBuyQuote": "sum"
    })
    valid_counts = input.resample(f'{tf_min}min').count()
    # in_re = in_re.where(valid_counts >= 10)
    in_re = in_re.dropna()
    in_re.reset_index(inplace=True)

    in_re.to_csv(write_path, compression="zip", index=False)


for tf_min in [2, 3, 5, 15, 30, 60, 240, 1440]:
    for_tf(tf_min)

input.to_csv(f"./{pair}_1.csv.zip", compression="zip", index=False)
