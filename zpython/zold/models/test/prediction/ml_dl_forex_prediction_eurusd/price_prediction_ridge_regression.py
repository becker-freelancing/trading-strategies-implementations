import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv("C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_1.csv.zip", compression="zip")
df["closeTime"] = pd.to_datetime(df["closeTime"])
df.set_index("closeTime", inplace=True)
max_time = df.index.max()

prediction_mask = (df.index > max_time - pd.Timedelta(minutes=30))
prediction = df[prediction_mask]["closeBid"]
prediction_values = prediction.values


def predict(num_in):
    in_mask = (df.index > max_time - pd.Timedelta(minutes=30 + num_in)) & (
                df.index <= max_time - pd.Timedelta(minutes=30))
    in_data = df[in_mask]["closeBid"]
    scaler = MinMaxScaler()
    in_values = in_data.values.reshape(-1, 1)
    xs = np.arange(len(in_data)).reshape(-1, 1)
    in_scaled = scaler.fit_transform(in_values)
    ridge = Ridge()
    ridge.fit(xs, in_scaled)
    pred_x = np.arange(start=len(in_data), stop=len(in_data) + 30)
    pred = ridge.predict(pred_x.reshape(-1, 1))
    pred = scaler.inverse_transform(pred)
    in_samp = ridge.predict(xs)
    in_samp = scaler.inverse_transform(in_samp)
    return xs.reshape(1, -1)[0], in_values.reshape(1, -1)[0], pred_x.reshape(1, -1)[0], pred.reshape(1, -1)[0], \
    in_samp.reshape(1, -1)[0]


xs, in_vals, pred_xs, pred, in_samp = predict(30)
plt.plot(xs, in_vals, label="Input")
plt.plot(xs, in_samp, label="In Sample Prediction")
plt.plot(pred_xs, pred, label="Actual")
plt.plot(pred_xs, prediction_values, label="Expected")
plt.legend()
plt.show()
