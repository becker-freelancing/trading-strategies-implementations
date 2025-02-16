import pandas as pd

df = pd.read_csv("C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_5.csv.zip", compression="zip")
df = df.iloc[1000000:]
data = df["closeBid"]

import numpy as np

# Berechnung der Log-Renditen -> Für Stationarität
returns = np.log(data / data.shift(1)).dropna()

from statsmodels.tsa.stattools import adfuller

result = adfuller(returns)
print(f"ADF-Statistik: {result[0]}")
print(f"p-Wert: {result[1]}")
# Ein p-Wert < 0.05 deutet in der Regel auf Stationarität hin.

from statsmodels.tsa.stattools import acf

# Berechne Autokorrelationswerte für z. B. 20 Lags
acf_values = acf(returns, nlags=20)
print(acf_values)

# ACF visualisierung
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf

plot_acf(returns, lags=20)
plt.xlabel("Lag")
plt.ylabel("Autokorrelation")
plt.title("ACF-Plot der Log-Renditen")
plt.show()

# PACF visualisierung
from statsmodels.graphics.tsaplots import plot_pacf

plot_pacf(returns, lags=20)
plt.xlabel("Lag")
plt.ylabel("Partielle Autokorrelation")
plt.title("PACF-Plot der Log-Renditen")
plt.show()

from statsmodels.stats.diagnostic import acorr_ljungbox

lb_test = acorr_ljungbox(returns, lags=[10], return_df=True)
print(lb_test)
# Ein p-Wert < 0.05 deutet auf signifikante Autokorrelation hin.
