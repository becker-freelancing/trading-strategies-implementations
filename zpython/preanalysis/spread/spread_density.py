import matplotlib.pyplot as plt
import scipy.stats as stats

from zpython.util.ig_data_reader import read_data

PAIR = "GLD/USD M5"
FILENAME = "GLDUSD_5.csv"

df = read_data(FILENAME)

df["openSpread"] = df["openAsk"] - df["openBid"]
df["highSpread"] = df["highAsk"] - df["highBid"]
df["lowSpread"] = df["lowAsk"] - df["lowBid"]
df["closeSpread"] = df["closeAsk"] - df["closeBid"]
# 1. KDE-Schätzung der Wahrscheinlichkeitsdichte

df = df[df["openSpread"] < 4]
data = df["openSpread"].values
kde = stats.gaussian_kde(data)

# 2. Generierung neuer Zufallszahlen durch KDE
samples = kde.resample(size=len(df))[0]

# 3. Histogramm der Originaldaten und der generierten Daten plotten
plt.hist(data, density=True, alpha=0.5, label="Original")
plt.hist(samples, density=True, alpha=0.5, label="Generated")
plt.title(f"Spread for {PAIR}")
plt.xlabel("Spread")
plt.ylabel("Density")
plt.yscale("log")
plt.legend()
plt.show()
