import numpy as np
import pandas as pd
import statsmodels.api as sm

# Beispielzeitreihe erzeugen
np.random.seed(42)
n = 200
X = np.random.normal(0, 1, n)

# Y hängt von X_t-3 und X_t-100 ab
Y = np.concatenate([0.8 * X[:-3], np.zeros(3)])  # X_t-3
Y += 0.5 * np.roll(X, 100)  # X_t-100
Y += np.random.normal(0, 1, n)  # Rauschen
Y[:100] = np.random.normal(0, 1, 100)  # frühe Werte ohne Signal

# DataFrame
data = pd.DataFrame({'X': X, 'Y': Y})

# Lags erzeugen
data['X_lag3'] = data['X'].shift(3)
data['X_lag100'] = data['X'].shift(100)
data = data.dropna()

# Design-Matrix
X_design = data[['X_lag3', 'X_lag100']]
X_design = sm.add_constant(X_design)

# Zielvariable
y = data['Y']

# OLS schätzen
model = sm.OLS(y, X_design).fit()
print(model.summary())
