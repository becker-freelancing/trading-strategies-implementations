from zpython.util.hist_data_data_reader import read_data

write_path = "C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_5.csv.zip"
input = read_data("EURUSD_1.csv.zip")

in_re = input.resample('5min').agg({
    "openBid": "first",
    "openAsk": "first",
    "highBid": "max",
    "highAsk": "max",
    "lowBid": "min",
    "lowAsk": "min",
    "closeBid": "last",
    "closeAsk": "last"
})
valid_counts = input.resample('5min').count()
in_re = in_re.where(valid_counts >= 3)
in_re = in_re.dropna()
in_re.reset_index(inplace=True)

in_re.to_csv(write_path, compression="zip", index=False)
