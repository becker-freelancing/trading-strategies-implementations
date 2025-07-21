import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from zpython.util.data_split import validation_data
import pandas_ta as ta

val = validation_data().iloc[:200]

close = val["closeBid"]
ema = ta.ema(close, 20)
sma = ta.sma(close, 20)

plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 18
})

plt.plot(close, label="Closing Price", color="black")
plt.plot(ema, label="EMA(20)")
plt.plot(sma, label="SMA(20)")
plt.legend()
plt.show()
