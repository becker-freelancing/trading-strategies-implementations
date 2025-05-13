import matplotlib

matplotlib.use("TkAgg")
import pandas as pd
from statsmodels.tsa.api import VAR
import matplotlib.pyplot as plt
from zpython.util import analysis_data
from zpython.indicators import create_multiple_indicators
import numpy as np
import warnings

df = create_multiple_indicators(analysis_data, limit=400)
df = df.replace([np.inf, -np.inf], np.nan).dropna()
actual = create_multiple_indicators(analysis_data, limit=430)


def predict(lag):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        model = VAR(df)
        var_result = model.fit(lag)
        forecast = var_result.forecast(df[-lag:].values, steps=30)
        return forecast[:, 7]


actual = actual.loc[df.index.max() + pd.Timedelta(minutes=1):df.index.max() + pd.Timedelta(minutes=31)][
    "logReturn_closeBid_1min"].values
plt.plot(range(31), actual, linestyle="dashed", label="Actual")  # plot act
for l in range(5, 100, 5):
    prediction = predict(l)
    print(f"Lag = {l} \t Mean = {np.mean(prediction)} \t Var = {np.var(prediction)}")
    plt.plot(range(30), prediction, label=f"Lag {l}")

plt.legend()
plt.grid()
plt.show()
