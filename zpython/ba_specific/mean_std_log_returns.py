import numpy as np

from zpython.util.data_split import train_data, test_data, backtest_data, validation_data

train = train_data()
test = test_data()
backtest = backtest_data()
validation = validation_data()

train = np.log(train["closeBid"] / train["closeBid"].shift(1))
test = np.log(test["closeBid"] / test["closeBid"].shift(1))
backtest = np.log(backtest["closeBid"] / backtest["closeBid"].shift(1))
validation = np.log(validation["closeBid"] / validation["closeBid"].shift(1))

print(f"Train - Mean: {np.mean(train)}, Std: {np.std(train)}")
print(f"Val - Mean: {np.mean(validation)}, Std: {np.std(validation)}")
print(f"Test - Mean: {np.mean(test)}, Std: {np.std(test)}")
print(f"Backtest - Mean: {np.mean(backtest)}, Std: {np.std(backtest)}")
