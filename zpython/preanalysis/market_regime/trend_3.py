import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pandas_ta as ta

from zpython.util import analysis_data
import warnings
from zpython.util import split_on_gaps

warnings.filterwarnings('ignore')

print("Read data")
df = analysis_data()
print("Create indicators")

df = split_on_gaps(df, 1)[1]
df = df.reset_index(drop=True)
df = df[["closeBid"]]

plt.plot(df.index, df["closeBid"], label="Close", c="black")

for p in [10, 150]:
    ma = ta.ema(df["closeBid"], length=p)
    ma_diff = (ma - ma.shift(1)) < 0
    ma_switch = ma_diff != ma_diff.shift(1)
    plt.scatter(ma_switch.index[ma_switch == True], ma.loc[ma_switch == True], label=f"MA({p}) switch")
    plt.plot(df.index, ma, label=f"MA({p})")

    ma = ta.sma(df["closeBid"], length=p)
    plt.plot(df.index, ma, label=f"SMA({p})")
    ma_diff = (ma - ma.shift(1)) < 0
    ma_switch = ma_diff != ma_diff.shift(1)
    plt.scatter(ma_switch.index[ma_switch == True], ma.loc[ma_switch == True], label=f"SMA({p}) switch")

plt.legend()
plt.show()
