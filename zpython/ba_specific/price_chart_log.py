import matplotlib

matplotlib.use("TkAgg")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from zpython.util.data_split import train_data, validation_data, test_data, backtest_data

train: pd.DataFrame = train_data()
validation = validation_data()
test = test_data()
backtest = backtest_data()

train["closeBid"] = np.log(train["closeBid"] / train["closeBid"].shift(1))
validation["closeBid"] = np.log(validation["closeBid"] / validation["closeBid"].shift(1))
test["closeBid"] = np.log(test["closeBid"] / test["closeBid"].shift(1))
backtest["closeBid"] = np.log(backtest["closeBid"] / backtest["closeBid"].shift(1))

print(f"mean train = {train['closeBid'].mean()}")
print(f"std train = {train['closeBid'].std()}")
print(f"mean validation = {validation['closeBid'].mean()}")
print(f"std validation = {validation['closeBid'].std()}")
print(f"mean test = {test['closeBid'].mean()}")
print(f"std test = {test['closeBid'].std()}")
print(f"mean backtest = {backtest['closeBid'].mean()}")
print(f"std backtest = {backtest['closeBid'].std()}")
plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20
})
plt.plot(train["closeTime"], train["closeBid"],
         label=f"Train (Mean: {round(train['closeBid'].mean(), 3)}, Std: {round(train['closeBid'].std(), 3)})")
plt.plot(validation["closeTime"], validation["closeBid"],
         label=f"Validation (Mean: {round(validation['closeBid'].mean(), 3)}, Std: {round(validation['closeBid'].std(), 3)})")
plt.plot(test["closeTime"], test["closeBid"],
         label=f"Test (Mean: {round(test['closeBid'].mean(), 3)}, Std: {round(test['closeBid'].std(), 3)})")
plt.plot(backtest["closeTime"], backtest["closeBid"],
         label=f"Backtest (Mean: {round(backtest['closeBid'].mean(), 3)}, Std: {round(backtest['closeBid'].std(), 3)})")

# plt.plot([train["closeTime"].min(), train["closeTime"].max()], [train["closeBid"].mean(), train["closeBid"].mean()])
# plt.plot([validation["closeTime"].min(), validation["closeTime"].max()], [validation["closeBid"].mean(), validation["closeBid"].mean()])
# plt.plot([test["closeTime"].min(), test["closeTime"].max()], [test["closeBid"].mean(), test["closeBid"].mean()])
# plt.plot([backtest["closeTime"].min(), backtest["closeTime"].max()], [backtest["closeBid"].mean(), backtest["closeBid"].mean()])

plt.title("Log Returns of ETH/USDC M1")
plt.ylabel("Log Returns [USDC]")
plt.legend()
plt.show()
