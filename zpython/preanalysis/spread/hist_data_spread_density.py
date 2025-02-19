import joblib
import matplotlib.pyplot as plt
import scipy.stats as stats

from zpython.util.hist_data_data_reader import read_data
from zpython.util.path_util import from_relative_path

PAIR = "EUR/USD M1"
BID_ASK_FILE_NAME = "EURUSD_TICK_BID_ASK.csv.zip"

bid_ask = read_data(BID_ASK_FILE_NAME)

bid_ask["spread"] = abs(bid_ask["closeAsk"] - bid_ask["closeBid"])
# 1. KDE-Schätzung der Wahrscheinlichkeitsdichte

bid_ask["spread"] = round(bid_ask["spread"], 5)
data = bid_ask["spread"].values
kde = stats.gaussian_kde(data)

# 2. Generierung neuer Zufallszahlen durch KDE
samples = kde.resample(size=len(bid_ask))[0]

# 3. Histogramm der Originaldaten und der generierten Daten plotten
plt.hist(data, density=True, alpha=0.5, label="Original")
plt.hist(samples, density=True, alpha=0.5, label="Generated")
plt.title(f"Spread for {PAIR}")
plt.xlabel("Spread")
plt.ylabel("Density")
plt.yscale("log")
plt.legend()
plt.show()

joblib.dump(kde, from_relative_path("spreadmodelation/gaussian_kde_scipy_eurusd_1_hist_data.dump"))
