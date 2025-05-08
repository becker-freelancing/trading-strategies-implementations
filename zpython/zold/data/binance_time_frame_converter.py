import pandas as pd

from zpython.util.path_util import from_relative_path

pair = "ETHUSDT"

input = pd.read_csv(from_relative_path(f"data-bybit/{pair}_1.csv"))
input["closeTime"] = pd.to_datetime(input["closeTime"])
input.set_index("closeTime", inplace=True)


def for_tf(tf_min):
    write_path = from_relative_path(f"data-bybit/{pair}_{tf_min}.csv")
    in_re = input.resample(f'{tf_min}min').agg({
        "openBid": "first",
        "openAsk": "first",
        "highBid": "max",
        "highAsk": "max",
        "lowBid": "min",
        "lowAsk": "min",
        "closeBid": "last",
        "closeAsk": "last",
        "volume": "sum"
    })
    in_re = in_re.dropna()
    in_re.reset_index(inplace=True)

    in_re.to_csv(write_path, index=False)


for tf_min in [2, 3, 5, 15, 30, 60, 240, 1440]:
    for_tf(tf_min)

