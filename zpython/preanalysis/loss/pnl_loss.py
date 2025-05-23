import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np

# Beispiel-Daten
np.random.seed(42)
returns = np.random.normal(0, 0.002, size=30)
preds = np.random.normal(0, 0.002, size=30)

returns_cum = np.cumsum(returns)
preds_cum = np.cumsum(preds)

plt.plot(returns, label="Actual Returns")
plt.plot(preds, label="Predicted Returns")
plt.plot(returns_cum, label="Cumulative Actual Returns")
plt.plot(preds_cum, label="Cumulative Predicted Returns")
plt.legend()
plt.show()
