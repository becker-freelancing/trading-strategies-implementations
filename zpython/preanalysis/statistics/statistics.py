import pandas as pd

from zpython.util.data_split import train_data, analysis_data, validation_data, test_data, backtest_data

train: pd.DataFrame = train_data()
analysis = analysis_data()
validation = validation_data()
test = test_data()
backtest = backtest_data()

train = train[["openBid", "highBid", "lowBid", "closeBid", "volume"]]
analysis = analysis[["openBid", "highBid", "lowBid", "closeBid", "volume"]]
validation = validation[["openBid", "highBid", "lowBid", "closeBid", "volume"]]
test = test[["openBid", "highBid", "lowBid", "closeBid", "volume"]]
backtest = backtest[["openBid", "highBid", "lowBid", "closeBid", "volume"]]

train = train.rename(
    columns={"openBid": "Open", "highBid": "High", "lowBid": "Low", "closeBid": "Close", "volume": "Volume"})
analysis = analysis.rename(
    columns={"openBid": "Open", "highBid": "High", "lowBid": "Low", "closeBid": "Close", "volume": "Volume"})
validation = validation.rename(
    columns={"openBid": "Open", "highBid": "High", "lowBid": "Low", "closeBid": "Close", "volume": "Volume"})
test = test.rename(
    columns={"openBid": "Open", "highBid": "High", "lowBid": "Low", "closeBid": "Close", "volume": "Volume"})
backtest = backtest.rename(
    columns={"openBid": "Open", "highBid": "High", "lowBid": "Low", "closeBid": "Close", "volume": "Volume"})

train.describe().to_csv("./train.csv")
analysis.describe().to_csv("./analysis.csv")
validation.describe().to_csv("./validation.csv")
test.describe().to_csv("./test.csv")
backtest.describe().to_csv("./backtest.csv")
