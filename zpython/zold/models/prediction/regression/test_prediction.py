import matplotlib

matplotlib.use('TkAgg')

from zpython.backtest_prediction.cnn_model_prediction import CnnModelPrediction
import matplotlib.pyplot as plt
import pandas as pd

predictor = CnnModelPrediction(bars_to_predict=100)

prediction = predictor.predict(26)

data = predictor.data_reader(predictor.data_source.file_path(predictor.pair))
pred_close = prediction.iloc[0]["closeTime"]
input = data.loc[pred_close - pd.Timedelta(minutes=100):pred_close]["closeBid"]
exp_output = data.loc[pred_close:pred_close + pd.Timedelta(minutes=30)]["closeBid"]
actual_output = prediction.iloc[0]["prediction"]
out_range = pd.date_range(start=pred_close,
                          end=pred_close + pd.Timedelta(minutes=(predictor.pair.minutes() * (len(actual_output) - 1))),
                          freq="min")

plt.plot(input, label="Input")
plt.plot(exp_output, label="Expected")
plt.plot(out_range, actual_output, label="Actual", color="blue", linestyle="--")
plt.legend()
plt.show()
