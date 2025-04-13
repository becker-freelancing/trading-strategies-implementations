import numpy as np
import pandas as pd

# Beispiel-Zeitreihe
np.random.seed(42)
data_length = 1000
df = pd.DataFrame({'Zeitreihe': np.cumsum(np.random.randn(data_length))})

# Fenstergröße definieren
window_size = 50  # Länge des Ausschnitts
lag = 1  # Wie viele Schritte rückwärts betrachtet werden

# Gleitende Autokorrelation berechnen
df['Rolling_Autocorr'] = df['Zeitreihe'].rolling(window=window_size).corr_sub(df['Zeitreihe'].shift(lag))

print(df[['Zeitreihe', 'Rolling_Autocorr']])

from statsmodels.tsa.stattools import acf

# Anzahl der Segmente (z. B. 100)
num_segments = 100
segment_size = len(df) // num_segments  # Länge jedes Segments
max_lag = 10  # Maximale Verzögerung

# Berechnung der Autokorrelation für jedes Segment
acf_results = []
for i in range(0, len(df), segment_size):
    segment = df.iloc[i:i + segment_size]['Zeitreihe']
    if len(segment) == segment_size:
        acf_values = acf(segment, nlags=max_lag)  # Autokorrelation für das ganze Segment
        acf_results.append(acf_values)

# In DataFrame umwandeln
acf_df = pd.DataFrame(acf_results, columns=[f'Lag_{i}' for i in range(max_lag)])

print(acf_df)

import matplotlib.pyplot as plt

plt.figure(figsize=(10, 5))
plt.plot(df['Rolling_Autocorr'], label=f'Gleitende Autokorrelation (Window={window_size}, Lag={lag})')
plt.xlabel("Zeit")
plt.ylabel("Autokorrelation")
plt.title("Gleitende Autokorrelation über die Zeit")
plt.legend()
plt.show()

plt.plot(acf_df['Lag_1'], marker='o', linestyle='-', label="Autokorrelation bei Lag 1")
plt.xlabel("Segment")
plt.ylabel("Autokorrelation")
plt.title("Autokorrelation pro Segment")
plt.legend()
plt.show()
