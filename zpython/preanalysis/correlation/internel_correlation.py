import numpy as np
import pandas as pd

# Beispiel-Zeitreihe generieren
np.random.seed(42)
data_length = 1000  # Länge der Zeitreihe
df = pd.DataFrame({'Zeitreihe': np.cumsum(np.random.randn(data_length))})  # Kumulierte Zufallswerte

# Anzahl der Segmente (100 Abschnitte)
num_segments = 100
segment_size = len(df) // num_segments  # Größe eines Segments


# Funktion zur Berechnung der Autokorrelation mit einem bestimmten Lag
def autocorr(series, lag=1):
    return series.autocorr(lag=lag)


# Berechnung der Autokorrelation für jedes Segment
autocorrelations = []
lag = 1  # Anzahl der Schritte, um die die Zeitreihe verschoben wird
for i in range(0, len(df), segment_size):
    segment = df.iloc[i:i + segment_size]['Zeitreihe']
    if len(segment) == segment_size:  # Sicherstellen, dass das Segment voll ist
        autocorrelations.append(autocorr(segment, lag=lag))

# Ergebnisse als Pandas-Serie speichern
autocorrelation_series = pd.Series(autocorrelations)

# Ausgabe der internen Autokorrelation pro Segment
print(autocorrelation_series)

import matplotlib.pyplot as plt

plt.plot(autocorrelation_series)
plt.xlabel("Segment-Nummer")
plt.ylabel("Autokorrelation")
plt.title("Interne Autokorrelation pro Segment")
plt.show()

from statsmodels.tsa.stattools import acf

lags = 20  # Anzahl der Lags, die betrachtet werden sollen
acf_values = acf(df['Zeitreihe'], nlags=lags)

# Plotten der Autokorrelationswerte
plt.stem(range(lags + 1), acf_values)
plt.xlabel("Lag")
plt.ylabel("Autokorrelation")
plt.title("Autokorrelationsfunktion (ACF)")
plt.show()
