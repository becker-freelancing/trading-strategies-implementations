from zpython.util.hist_data_data_reader import read_data

input = read_data("EURUSD_1.csv.zip")


def for_tf(tf_min):
    write_path = f"C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_{tf_min}.csv.zip"
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

    in_re.to_csv(write_path, compression="zip", index=False)


for tf_min in [5, 15, 30, 60, 1440]:
    for_tf(tf_min)
