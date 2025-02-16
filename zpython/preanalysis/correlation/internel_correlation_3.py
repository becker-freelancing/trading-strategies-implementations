import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf

# Beispielzeitreihe
df = pd.read_csv("C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_5.csv.zip", compression="zip")
data = df["closeBid"].to_numpy()

# Autokorrelation plotten
plot_acf(data, lags=50)
# plt.show()

from statsmodels.graphics.tsaplots import plot_pacf

plot_pacf(data, lags=50)
plt.show()
