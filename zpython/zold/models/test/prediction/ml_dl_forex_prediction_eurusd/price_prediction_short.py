# https://www.kaggle.com/code/ashkanforootan/af-ml-dl-forex-prediction-eurusd

from datetime import date
# from sktime.forecasting.all import (
#         Deseasonalizer, Detrender,
#         temporal_train_test_split,
#         mean_absolute_percentage_error as mape,
#         mean_squared_percentage_error as mspe,
#         mean_squared_error as mse,
#         ForecastingHorizon,
#         NaiveForecaster,
#         TransformedTargetForecaster,
#         PolynomialTrendForecaster
# )
# from sktime.forecasting.compose import make_reduction
# from sktime.forecasting.all import (
#         ForecastingGridSearchCV,
#         SlidingWindowSplitter,
#         MeanAbsolutePercentageError)
# from sktime.performance_metrics.forecasting import(MeanAbsolutePercentageError,
#                                                    MeanSquaredError,
#                                                    MeanAbsoluteScaledError)
from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

# import warnings
# warnings.filterwarnings('ignore')
# import sktime

# mse = MeanSquaredError()
# mape = MeanAbsolutePercentageError()
# mase = MeanAbsoluteScaledError()
# from sktime.forecasting.all import EnsembleForecaster

# from sktime.transformations.series.detrend import ConditionalDeseasonalizer
# from sktime.datasets import load_macroeconomic


###### configurations for image quality#######
plt.rcParams["figure.figsize"] = [20, 8]  ##
# plt.rcParams['figure.dpi'] = 300           ## 300 for printing
plt.rc('font', size=8)  ##
plt.rc('axes', titlesize=16)  ##
plt.rc('axes', labelsize=14)  ##
plt.rc('xtick', labelsize=10)  ##
plt.rc('ytick', labelsize=10)  ##
plt.rc('legend', fontsize=10)  ##
plt.rc('figure', titlesize=12)  ##
#############################################

today = date.today()
print("Today's date:", today)

TwoLastCandle = today - timedelta(minutes=3)
LastCandle = today - timedelta(minutes=7)

print("TwoLastCandle : ", TwoLastCandle)
print("LastCandle : ", LastCandle)

df = pd.read_csv("C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_1.csv.zip", compression="zip")
df["closeTime"] = pd.to_datetime(df["closeTime"])
df.set_index("closeTime", inplace=True)
max = df.index.max()
Symbol = df[(df.index > pd.to_datetime("2020-01-01")) & (df.index <= max - pd.Timedelta(minutes=3))]["closeBid"]
Symbol_LastCandle = df[(df.index == max - pd.Timedelta(minutes=8)) | (df.index == max - pd.Timedelta(minutes=7))][
    "closeBid"]

print(f"{Symbol_LastCandle=}")

best_model = pd.DataFrame({'Model': [], 'Prediction': []})

best_model.loc[len(best_model.index)] = ["***Real Today Price***", float(Symbol_LastCandle.iloc[-1])]
best_model.loc[len(best_model.index)] = ["***Real Last_day Price***", float(Symbol_LastCandle.iloc[-2])]

Symbol.columns = ['y']
print(f"{Symbol=}")

Symbol.plot(title='Symbol close price')


def handle_missing_data(df):
    n = int(df.isna().sum())
    if n > 0:
        print(f'found {n} missing observations...')
        df.ffill(inplace=True)
    else:
        print('no missing data')


Symbol_copy = Symbol.copy()
handle_missing_data(Symbol_copy)

print(f"{Symbol_copy.isna().sum()=}")


def one_step_forecast(df, window):
    d = df.values
    x = []
    n = len(df)
    idx = df.index[:-window]
    for start in range(n - window):
        end = start + window
        x.append(d[start:end])
    cols = [f'x_{i}' for i in range(1, window + 1)]
    x = np.array(x).reshape(n - window, -1)
    y = df.iloc[window:].values
    df_xs = pd.DataFrame(x, columns=cols, index=idx)
    df_y = pd.DataFrame(y.reshape(-1), columns=['y'], index=idx)
    return pd.concat([df_xs, df_y], axis=1).dropna()


Symbol_os = one_step_forecast(Symbol_copy, 5)

print(f"{Symbol_os.shape=}")

print(f"{Symbol_copy.tail(10)=}")

print(f"{Symbol_os.tail(10)=}")

print(f"{Symbol_copy.tail(5)=}")


def insert(df, row):
    insert_loc = df.index.max()

    if pd.isna(insert_loc):
        df.loc[0] = row
    else:
        df.loc[insert_loc + 1] = row


def split_data(df, test_split=0.15):
    n = int(len(df) * test_split)
    train, test = df[:-n], df[-n:]
    return train, test


train, test = split_data(Symbol_os)
print(f'Train: {len(train)}, Test: {len(test)}')


class Standardize:
    def __init__(self, split=0.15):
        self.split = split

    def _transform(self, df):
        return (df - self.mu) / self.sigma

    def split_data(self, df):
        n = int(len(df) * self.split)
        train, test = df[:-n], df[-n:]
        return train, test

    def fit_transform(self, train, test):
        self.mu = train.mean()
        self.sigma = train.std()
        train_s = self._transform(train)
        test_s = self._transform(test)
        return train_s, test_s

    def transform(self, df):
        return self._transform(df)

    def inverse(self, df):
        return (df * self.sigma) + self.mu

    def inverse_y(self, df):
        return (df * self.sigma[0]) + self.mu[0]


scaler = Standardize()
train_s, test_s = scaler.fit_transform(train, test)
print(f"{train_s.head()=}")

y_train_original = scaler.inverse_y(train_s['y'])

train_original = scaler.inverse(train_s)
print(f"{train_original.head()=}")

df = Symbol.copy()

Symbol_copy = Symbol.copy()
handle_missing_data(Symbol_copy)

Symbol_reg = one_step_forecast(Symbol_copy, 10)

df_tomorrow = pd.DataFrame(data=None, columns=Symbol_reg.columns)
insert(df_tomorrow, [float(Symbol_reg.iloc[-1].loc['x_2']), float(Symbol_reg.iloc[-1].loc['x_3']),
                     float(Symbol_reg.iloc[-1].loc['x_4']), \
                     float(Symbol_reg.iloc[-1].loc['x_5']), float(Symbol_reg.iloc[-1].loc['x_6']),
                     float(Symbol_reg.iloc[-1].loc['x_7']), \
                     float(Symbol_reg.iloc[-1].loc['x_8']), float(Symbol_reg.iloc[-1].loc['x_9']),
                     float(Symbol_reg.iloc[-1].loc['x_10']), \
                     float(Symbol_reg.iloc[-1].loc['y']), 0])
df_tomorrow["date"] = Symbol_reg.index[-1] + timedelta(days=1)
df_tomorrow.set_index('date', inplace=True)

print(f"{df_tomorrow=}")

print(Symbol_reg.shape)

from sklearn import metrics

train_Symbol, test_Symbol = split_data(Symbol_reg, test_split=0.10)
scaler_Symbol = Standardize()
train_Symbol_s, test_Symbol_s = scaler_Symbol.fit_transform(train_Symbol, test_Symbol)

ridge = Ridge(1, fit_intercept=False)

x_tomorrow = df_tomorrow.drop(columns=['y'])


def train_model(train, test, regressor, reg_name):
    X_train, y_train = train.drop(columns=['y']), train['y']
    X_test, y_test = test.drop(columns=['y']), test['y']

    print(f'training {reg_name} ...')

    regressor.fit(X_train, y_train)
    #     print (regressor)
    yhat = regressor.predict(X_test)
    #     print(X_test)
    #     print(X_test.shape)
    #     print(x_tomorrow.shape)
    y_tomorrow = regressor.predict(x_tomorrow)
    #     y_tomorrow = 0
    rmse_test = np.sqrt(metrics.mean_squared_error(y_test, yhat))
    mae_test = metrics.mean_absolute_error(y_test, yhat)
    mse_test = metrics.mean_squared_error(y_test, yhat)
    r2_test = metrics.r2_score(y_test, yhat)
    residuals = y_test.values - yhat

    model_metadata = {
        'Model Name': reg_name, 'Model': regressor,
        'RMSE': rmse_test, 'MAE': mae_test, 'MSE': mse_test, 'R2': r2_test,
        'yhat': yhat, 'resid': residuals, 'actual': y_test.values, "y_tomorrow": float(y_tomorrow)}

    return model_metadata


Symbol_results = train_model(train_Symbol_s, test_Symbol_s, ridge, "Ridge")

cols = ['Model Name', 'RMSE', 'MAE', 'MSE', 'R2']
Symbol_results = pd.DataFrame(Symbol_results)
Symbol_results[cols].sort_values('R2', ascending=False).style.background_gradient(cmap='summer_r')

print(f"{Symbol.tail(5)=}")

print(f"{Symbol_LastCandle=}")

print("Real Price : ", float(Symbol_LastCandle.iloc[-1]))

cols = ['Model Name', "y_tomorrow"]
Symbol_results = pd.DataFrame(Symbol_results)
Symbol_results[cols].sort_values('y_tomorrow', ascending=False).style.background_gradient(cmap='summer_r')

for i in range(0, len(Symbol_results)):
    best_model.loc[len(best_model.index)] = [Symbol_results["Model Name"].iloc[i], Symbol_results['y_tomorrow'].iloc[i]]

from statsmodels.graphics.tsaplots import plot_acf


def plot_results(cols, results, data_name):
    for row in results[cols].iterrows():
        yhat, resid, actual, name = row[1]
        plt.title(f'{data_name} - {name}')
        plt.plot(actual, 'k--', alpha=0.5)
        plt.plot(yhat, 'k')
        plt.legend(['actual', 'forecast'])
        plot_acf(resid, zero=False,
                 title=f'{data_name} - Autocorrelation')
        plt.show()


cols = ['yhat', 'resid', 'actual', 'Model Name']
plot_results(cols, Symbol_results, 'Symbol')

df_tomorrow = pd.DataFrame(data=None, columns=Symbol_reg.columns)
df_tomorrow["date"] = None
for i in range(1, 4):
    insert(df_tomorrow, [float(Symbol_reg.iloc[-i].loc['x_2']), float(Symbol_reg.iloc[-i].loc['x_3']),
                         float(Symbol_reg.iloc[-i].loc['x_4']), \
                         float(Symbol_reg.iloc[-i].loc['x_5']), float(Symbol_reg.iloc[-i].loc['x_6']),
                         float(Symbol_reg.iloc[-i].loc['x_7']), \
                         float(Symbol_reg.iloc[-i].loc['x_8']), float(Symbol_reg.iloc[-i].loc['x_9']),
                         float(Symbol_reg.iloc[-i].loc['x_10']), \
                         float(Symbol_reg.iloc[-i].loc['y']), float(Symbol_reg.iloc[-i].loc['y']),
                         Symbol_reg.index[-i] + timedelta(days=1)])

#     df_tomorrow["date"] = Symbol_reg.index[-1]+ timedelta(days=1)
df_tomorrow.set_index('date', inplace=True)

print(f"{df_tomorrow=}")
