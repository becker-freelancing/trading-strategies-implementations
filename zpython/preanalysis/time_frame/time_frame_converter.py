import pandas as pd

pair = "BTCPERP"

input = pd.read_csv(f"C:/Users/jasb/AppData/Roaming/krypto-java/data-bybit/{pair}_1.csv")
input["closeTime"] = pd.to_datetime(input["closeTime"])
input.set_index("closeTime", inplace=True)


def for_tf(tf_min):
    write_path = f"C:/Users/jasb/AppData/Roaming/krypto-java/data-bybit/{pair}_{tf_min}.csv"
    in_re = input.resample(f'{tf_min}min').agg({
        "openBid": "first",
        "openAsk": "first",
        "highBid": "max",
        "highAsk": "max",
        "lowBid": "min",
        "lowAsk": "min",
        "closeBid": "last",
        "closeAsk": "last"
    })
    valid_counts = input.resample(f'{tf_min}min').count()
    # in_re = in_re.where(valid_counts >= 10)
    in_re = in_re.dropna()
    in_re.reset_index(inplace=True)

    in_re.to_csv(write_path, index=False)


for tf_min in [5, 15, 30, 60, 1440]:
    for_tf(tf_min)
