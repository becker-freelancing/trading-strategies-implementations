import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.vector_ar.var_model import VARResultsWrapper

from zpython.indicators import create_multiple_indicators
from zpython.util import from_relative_path, analysis_data

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
    names = []
    lags = []
    best = features.loc[[f"Best_{n}" for n in range(N_BEST)]]
    for idx, b in best.iterrows():
        caused = eval(b[f"CausedLag_{future_idx}"])
        names.append(caused[0])
        lags.append(int(caused[1]))
    predict_df = pd.DataFrame(columns=names)
    for name, lag in zip(names, lags):
        predict_df[name] = data[name].shift(lag)
    predict_df = predict_df.dropna()
    y = data.loc[predict_df.index][["logReturn_closeBid_1min"]].shift(-future_idx)
    y = y.dropna()
    predict_df = predict_df.loc[y.index]
    return predict_df.reset_index(drop=True), y.reset_index(drop=True)


def predict(model: VARResultsWrapper, idx):
    x, y = get_predict_df(idx)
    prediction = model.forecast(y=predict_df.values[-model.k_ar:], steps=1)[0][10]
    return prediction


splitIdx = data.index.max() - pd.Timedelta(minutes=40)
fitted = [fit(idx, splitIdx) for idx in range(30)]
predicted = [predict(model, idx) for idx, model in zip(range(30), fitted)]
