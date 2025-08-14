import matplotlib

matplotlib.use("TkAgg")
import pandas as pd
import matplotlib.pyplot as plt

from zpython.util.data_split import train_data, validation_data, test_data, backtest_data

train: pd.DataFrame = train_data()
validation = validation_data()
test = test_data()
backtest = backtest_data()

plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20
})

plt.plot(train["closeTime"], train["closeBid"], label="Train")
plt.plot(validation["closeTime"], validation["closeBid"], label="Validation")
plt.plot(test["closeTime"], test["closeBid"], label="Test")
plt.plot(backtest["closeTime"], backtest["closeBid"], label="Backtest")

# plt.plot([train["closeTime"].min(), train["closeTime"].max()], [train["closeBid"].mean(), train["closeBid"].mean()])
# plt.plot([validation["closeTime"].min(), validation["closeTime"].max()], [validation["closeBid"].mean(), validation["closeBid"].mean()])
# plt.plot([test["closeTime"].min(), test["closeTime"].max()], [test["closeBid"].mean(), test["closeBid"].mean()])
# plt.plot([backtest["closeTime"].min(), backtest["closeTime"].max()], [backtest["closeBid"].mean(), backtest["closeBid"].mean()])

plt.title("ETH/USDC M1")
plt.ylabel("Price [USDC]")
plt.xlabel("Date")
plt.legend()
plt.show()
