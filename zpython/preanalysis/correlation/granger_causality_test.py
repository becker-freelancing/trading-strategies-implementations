import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.vector_ar.var_model import VARResultsWrapper

from zpython.util import from_relative_path, analysis_data
from zpython.util.indicator_creator import create_multiple_indicators

N_BEST = 10

features = pd.read_csv(from_relative_path("analysis-bybit/granger/granger_test_1_analysis.csv"))
features.set_index("index", inplace=True)

data = create_multiple_indicators(data_read_function=analysis_data, limit=500)


def fit(future_idx, splitIdx):
    X, y = get_predict_df(future_idx, splitIdx)
    var = sm.OLS(endog=y, exog=X)
    var = var.fit(maxlags=100)

    return var


def get_predict_df(future_idx, splitIdx):
    work_data = data.loc[:splitIdx]
    names = []
    lags = []
    best = features.loc[[f"Best_{n}" for n in range(N_BEST)]]
    for idx, b in best.iterrows():
        caused = eval(b[f"CausedLag_{future_idx}"])
        names.append(caused[0])
        lags.append(int(caused[1]))
    predict_df = pd.DataFrame(columns=names)
    for name, lag in zip(names, lags):
        series = work_data[name]
        shifted = series.shift(lag)
        predict_df[name] = shifted
    predict_df = predict_df.dropna()
    y_raw = data.loc[predict_df.index + pd.Timedelta(minutes=future_idx)][["logReturn_closeBid_1min"]]
    y_shifted = y_raw.shift(-future_idx)
    y = y_shifted.dropna()
    predict_df = predict_df.loc[y.index]
    return sm.add_constant(predict_df.reset_index(drop=True)), y.reset_index(drop=True)


def predict(model: VARResultsWrapper, future_idx, splitIdx):
    x, y = get_predict_df(future_idx, splitIdx)
    prediction = model.predict(x)
    return prediction.iloc[-1]


splitIdx = data.index.max() - pd.Timedelta(minutes=40)
horizon = list(range(1, 30))
fitted = [fit(idx, splitIdx) for idx in horizon]
predicted = [predict(model, idx, splitIdx) for idx, model in zip(horizon, fitted)]
actual = [get_predict_df(idx, splitIdx)[1].iloc[-1]["logReturn_closeBid_1min"] for idx in horizon]

print(actual)
print(predicted)

plt.plot(horizon, actual, label="Actual")
plt.plot(horizon, predicted, label="Predicted")
plt.legend()
plt.grid()
plt.show()
