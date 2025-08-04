import numpy as np
from statsmodels.tsa.stattools import adfuller

from zpython.util.data_split import read_data

data = read_data(1, "ETHPERP")

log = np.log(data["closeBid"] / data["closeBid"].shift(1))

log = log.values[-1000000:]

res = adfuller(log)

print(res)

# 500k: (np.float64(-70.30713632478893), 0.0, 100, 499899, {'1%': np.float64(-3.4303630813095825), '5%': np.float64(-2.8615457817848604), '10%': np.float64(-2.5667730774328796)}, np.float64(-5411546.212476904))
