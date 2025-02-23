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
import pandas as pd
import seaborn as sns
from sklearn.linear_model import ElasticNet
from sklearn.linear_model import HuberRegressor
from sklearn.linear_model import Lasso
from sklearn.linear_model import LinearRegression
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

TwoLastCandle = today - timedelta(days=3)
LastCandle = today - timedelta(days=7)

print("TwoLastCandle : ", TwoLastCandle)
print("LastCandle : ", LastCandle)

# EURUSD=X
# GPBUSD=X

# symb = "GBPUSD=X"
#
# Symbol = yfinance.download(symb,
#                             start=datetime.datetime(2021, 1, 1),
#                             end=TwoLastCandle)['Close']
#
# Symbol_LastCandle = yfinance.download(symb,
#                                        start=LastCandle,
#                                        end=LastCandle)['Close']

df = pd.read_csv("C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_1.csv.zip", compression="zip")
df["closeTime"] = pd.to_datetime(df["closeTime"])
df.set_index("closeTime", inplace=True)
max = df.index.max()
Symbol = df[(df.index > pd.to_datetime("2020-01-01")) & (df.index <= max - pd.Timedelta(days=3))]["closeBid"]
Symbol_LastCandle = df[(df.index == max - pd.Timedelta(days=8)) | (df.index == max - pd.Timedelta(days=7))]["closeBid"]

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

# print ("Mean Absolute Error: ", metrics.mean_absolute_error(y_test , y_pred))
# print ("Mean Squared  Error: ", metrics.mean_squared_error(y_test , y_pred))
# print ("Root Absolute Error: ", np.sqrt(metrics.mean_squared_error(y_test , y_pred)))
# print ("R2 Score: ", metrics.r2_score(y_test , y_pred))

train_Symbol, test_Symbol = split_data(Symbol_reg, test_split=0.10)
scaler_Symbol = Standardize()
train_Symbol_s, test_Symbol_s = scaler_Symbol.fit_transform(train_Symbol, test_Symbol)

regressors = {
    'Linear Regression': LinearRegression(fit_intercept=False),
    'Elastic Net': ElasticNet(1, fit_intercept=False),
    'Ridge Regression': Ridge(1, fit_intercept=False),
    'Lasso Regression': Lasso(1, fit_intercept=False),
    'Huber Regression': HuberRegressor(fit_intercept=False)}

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


def train_different_models(train, test, regressors):
    results = []
    for reg_name, regressor in regressors.items():
        results.append(train_model(train,
                                   test,
                                   regressor,
                                   reg_name))
    return results


Symbol_results = train_different_models(train_Symbol_s, test_Symbol_s, regressors)

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

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import warnings

warnings.filterwarnings('ignore')
# plt.rc("figure", figsize=(16, 4))

import pytorch_lightning as pl
import torch

print(f'''
pandas -> {pd.__version__}   
numpy -> {np.__version__}
PyTorch Lightning -> {pl.__version__}
Torch -> {torch.__version__}
''')

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

print(f"{print(Symbol.index.freq)=}")

Symbol_cp = Symbol.copy()


def handle_missing_data(df):
    n = int(df.isna().sum())
    if n > 0:
        print(f'found {n} missing observations...')
        df.ffill(inplace=True)


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


def split_data(df, test_split=0.15):
    n = int(len(df) * test_split)
    train, test = df[:-n], df[-n:]
    return train, test


handle_missing_data(Symbol_cp)

Symbol_df = one_step_forecast(Symbol_cp, 10)

print(Symbol_df.shape)


class Standardize:
    def __init__(self, df, split=0.10):
        self.data = df
        self.split = split

    def split_data(self):
        n = int(len(self.data) * self.split)
        train, test = self.data.iloc[:-n], self.data.iloc[-n:]
        n = int(len(train) * self.split)
        train, val = train.iloc[:-n], train.iloc[-n:]
        assert len(test) + len(train) + len(val) == len(self.data)
        return train, test, val

    def _transform(self, data):
        data_s = (data - self.mu) / self.sigma
        return data_s

    def fit_transform(self):
        train, test, val = self.split_data()
        self.mu, self.sigma = train.mean(), train.std()
        train_s = self._transform(train)
        test_s = self._transform(test)
        val_s = self._transform(val)
        return train_s, test_s, val_s

    def inverse(self, data):
        return (data * self.sigma) + self.mu

    def inverse_y(self, data):
        return (data * self.sigma[-1]) + self.mu[-1]


scale_Symbol = Standardize(Symbol_df)

train_Symbol, test_Symbol, val_Symbol = scale_Symbol.fit_transform()

scale_df_tomorrow = Standardize(df_tomorrow, split=1)
train_Symbol_tomorrow, test_Symbol_tomorrow, val_Symbol_tomorrow = scale_df_tomorrow.fit_transform()
print(f'''
Symbol: train: {len(train_Symbol_tomorrow)} , test: {len(test_Symbol_tomorrow)}, val:{len(val_Symbol_tomorrow)}

''')
print(f"{test_Symbol_tomorrow=}")

print(f"{df_tomorrow=}")

print(f"{df_tomorrow.mean()=}")
print(f"{df_tomorrow.std()=}")

df_tomorrow_trns = (df_tomorrow - df_tomorrow.mean()) / df_tomorrow.std()
print(f"{df_tomorrow_trns.iloc[1]=}")

train_Symbol_pt, test_Symbol_pt, val_Symbol_pt = scale_Symbol.fit_transform()

print(f'''
Symbol: train: {len(train_Symbol)} , test: {len(test_Symbol)}, val:{len(val_Symbol)}

''')

import torch
import torch.nn as nn


def features_target_pt(*args):
    y = [torch.from_numpy(col.pop('y').values.reshape(-1, 1)).float() for col in args]
    x = [torch.from_numpy(col.values.reshape(*col.shape, 1)).float()
         for col in args]
    return (*y, *x)


(y_train_Symbol_pt,
 y_val_Symbol_pt,
 y_test_Symbol_pt,
 x_train_Symbol_pt,
 x_val_Symbol_pt,
 x_test_Symbol_pt) = features_target_pt(train_Symbol_pt,
                                        val_Symbol_pt,
                                        test_Symbol_pt)

print(train_Symbol_pt.shape,
      val_Symbol_pt.shape,
      test_Symbol_pt.shape)


def features_target_ts(*args):
    y = [col.pop('y').values.reshape(-1, 1) for col in args]
    x = [col.values.reshape(*col.shape, 1) for col in args]
    return (*y, *x)


(y_train_Symbol,
 y_val_Symbol,
 y_test_Symbol,
 x_train_Symbol,
 x_val_Symbol,
 x_test_Symbol) = features_target_ts(train_Symbol,
                                     val_Symbol,
                                     test_Symbol)

print(y_train_Symbol.shape,
      y_test_Symbol.shape,
      y_val_Symbol.shape)

from keras.api.models import Sequential
from keras.api.metrics import RootMeanSquaredError, MeanAbsoluteError
from keras.api.layers import (Dense,
                              LSTM, Dropout)


class RNN(nn.Module):
    def __init__(self, input_size, output_size, n_features, n_layers):
        super(RNN, self).__init__()
        self.n_layers = n_layers
        self.hidden_dim = n_features
        self.rnn = nn.RNN(input_size, n_features, n_layers, batch_first=True)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(n_features, output_size)

    def forward(self, x, hn):
        # batch_first=True -> (batch_size, seq_length, input_size)
        x = x.view(1, x.shape[0], x.shape[1])
        rnn_o, hn = self.rnn(x, hn)
        rnn_o = self.dropout(rnn_o)
        # reshape
        rnn_o = rnn_o.view(-1, self.hidden_dim)
        output = self.fc(rnn_o)
        return output, hn

    def init_hidden(self):
        weight = next(self.parameters()).data
        hidden = weight.new(self.n_layers, 1, self.hidden_dim).zero_()
        return hidden


class EarlyStopping:
    """Early stops the training if validation loss doesn't improve after a given patience."""

    def __init__(self, patience=7, verbose=False, delta=0, path='checkpoint.pt', trace_func=print):
        """
        Args:
            patience (int): How long to wait after last time validation loss improved.
                            Default: 7
            verbose (bool): If True, prints a message for each validation loss improvement.
                            Default: False
            delta (float): Minimum change in the monitored quantity to qualify as an improvement.
                            Default: 0
            path (str): Path for the checkpoint to be saved to.
                            Default: 'checkpoint.pt'
            trace_func (function): trace print function.
                            Default: print
        """
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
        self.path = path
        self.trace_func = trace_func
        self.best_score = None

    def __call__(self, val_loss, model):

        score = -val_loss

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score < self.best_score + self.delta:
            self.counter += 1
            #             self.trace_func(f'EarlyStopping counter: {self.counter} out of {self.patience}')
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        '''Saves model when validation loss decrease.'''
        #         if self.verbose:
        #             self.trace_func(f'Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ...')
        torch.save(model.state_dict(), self.path)
        self.val_loss_min = val_loss


def weight_reset(m):
    reset_parameters = getattr(m, "reset_parameters", None)
    if callable(reset_parameters):
        m.reset_parameters()


def train_model_pt(model_type='RNN', **kwargs):
    """
    Parameters:
        input_size: input size
        output_size: output size
        n_features: number of features (hidden dimension)
        n_layers: number of layers
        train_data: tuple ex (x_train, y_train)
        val_data: tuple ex (x_val, y_val)
        epochs: number of epochs
        print_every: output and history tracking
        lr: learning rate
    """
    # early stopping patience; how long to wait after last time validation loss improved.
    patience = 15
    early_stopping = EarlyStopping(patience=patience, verbose=True)
    #     model.apply(weight_reset)
    if model_type == 'RNN':
        model = RNN(kwargs['input_size'],
                    kwargs['output_size'],
                    kwargs['units'],
                    kwargs['n_layers'])
    elif model_type == 'LSTM':
        model = LSTM(kwargs['input_size'],
                     kwargs['output_size'],
                     kwargs['units'],
                     kwargs['n_layers'])
    elif model_type == 'GRU':
        model = LSTM(kwargs['input_size'],
                     kwargs['output_size'],
                     kwargs['units'],
                     kwargs['n_layers'])

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=kwargs['lr'])

    x_train, y_train = kwargs['train_data']
    x_val, y_val = kwargs['val_data']
    x_test, y_test = kwargs['test_data']

    history = {'loss': [], 'val_loss': []}
    # batch_size = x_train.shape[0]
    model.train()
    epochs = kwargs['epochs']
    print_every = kwargs['print_every']

    for batch_i, epoch in enumerate(range(epochs)):
        h = model.init_hidden()
        optimizer.zero_grad()
        pred, h = model(x_train, h)  # model(x_train)
        # hidden = hidden.data
        loss = criterion(pred, y_train)
        loss.backward()
        optimizer.step()

        if batch_i % print_every == 0:
            model.eval()
            with torch.no_grad():
                val_h = model.init_hidden()
                val_p, val_h = model(x_val, val_h)
                val_loss = criterion(val_p, y_val)
                history['val_loss'].append(val_loss.item())
            model.train()
            history['loss'].append(loss.item())
            print(f'{batch_i}/{epochs} - Loss:  {loss.item()}, val_loss: {val_loss.item()}')

        # early_stopping needs the validation loss to check if it has decresed,
        # and if it has, it will make a checkpoint of the current model
        early_stopping.__call__(val_loss, model)

        if batch_i > 20 and early_stopping.early_stop:
            print("Early stopping at epooch: ", batch_i)
            break

    ## Prediction
    model.eval()
    with torch.no_grad():
        h0 = model.init_hidden()
        y_hat = model(x_test, h0)
    y_hat, _ = y_hat
    mse_loss_air = criterion(y_hat, y_test)
    print(f'Test MSE Loss: {mse_loss_air.item():.4f}')

    ## Plotting
    fig, ax = plt.subplots(2, 1)

    ax[0].set_title(f'{model_type}: Loss and Validation Loss per epoch')
    ax[0].plot(history['loss'], 'k--', label='loss')
    ax[0].plot(history['val_loss'], 'k', label='val_loss')
    ax[0].legend()
    ax[1].set_title(f"{model_type} TEST MSE = {mse_loss_air.item():.4f}: Forecast vs Actual (Out-of-Sample data)")
    scale = kwargs['scale']
    actual = scale.inverse_y(y_test.detach().numpy().ravel())
    pred = scale.inverse_y(y_hat.detach().numpy().ravel())
    idx = kwargs['idx']
    pd.Series(actual, index=idx).plot(style='k--', label='actual', alpha=0.65)
    pd.Series(pred, index=idx).plot(style='k', label='forecast')
    fig.tight_layout()
    ax[1].legend();
    plt.show()

    return model, history


params_Symbol_pt = {'input_size': x_train_Symbol_pt.shape[1],
                    'output_size': 1,
                    'units': 32,
                    'n_layers': 1,
                    'epochs': 500,
                    'print_every': 25,
                    'lr': 0.01,
                    'train_data': (x_train_Symbol_pt, y_train_Symbol_pt),
                    'val_data': (x_val_Symbol_pt, y_val_Symbol_pt),
                    'test_data': (x_test_Symbol_pt, y_test_Symbol_pt),
                    'idx': test_Symbol_pt.index,
                    'scale': scale_Symbol}

import keras


def create_model(train, units, dropout=0.2):
    model = Sequential()
    model.add(keras.api.layers.LSTM(units=units,
                                    input_shape=(train.shape[1],
                                                 train.shape[2])))
    model.add(Dropout(dropout))
    model.add(Dense(1))

    return model


class LSTM(nn.Module):
    def __init__(self, input_size, output_size, n_features, n_layers):
        super(LSTM, self).__init__()
        self.n_layers = n_layers
        self.hidden_dim = n_features
        self.lstm = nn.LSTM(input_size, n_features, n_layers, batch_first=True)
        self.dropout = nn.Dropout(0.2)
        self.fc = nn.Linear(n_features, output_size)

    def forward(self, x, hn):
        # batch_first=True -> (batch_size, seq_length, input_size)
        x = x.view(1, x.shape[0], x.shape[1])
        lstm_o, hn = self.lstm(x, hn)
        lstm_o = self.dropout(lstm_o)
        # reshape
        lstm_o = lstm_o.view(-1, self.hidden_dim)
        output = self.fc(lstm_o)
        return output, hn

    def init_hidden(self):
        weight = next(self.parameters()).data
        hidden = (weight.new(self.n_layers, 1, self.hidden_dim).zero_(),
                  weight.new(self.n_layers, 1, self.hidden_dim).zero_())
        return hidden


def train_model_ts(model,
                   x_train, y_train, x_val, y_val,
                   epochs=10,
                   patience=15,
                   batch_size=32):
    model.compile(optimizer='adam',
                  loss='mean_squared_error',
                  metrics=[RootMeanSquaredError(),
                           MeanAbsoluteError(), r_two])

    es = keras.api.callbacks.EarlyStopping(
        monitor="r_two",
        min_delta=0,
        patience=patience,
        mode="max")

    history = model.fit(x_train, y_train,
                        shuffle=False, epochs=epochs,
                        batch_size=batch_size,
                        validation_data=(x_val, y_val),
                        callbacks=[es], verbose=1)
    return history


from keras.api import ops as backend


def r_two(y_true, y_pred):
    SSres = backend.sum(backend.sqrt(y_true - y_pred))
    SStot = backend.sum(backend.sqrt(y_true - backend.mean(y_true, axis=-1)))
    return 1 - SSres / SStot


def plot_forecast(model, x_test, y_test, index, history):
    fig, ax = plt.subplots(2, 1)
    (pd.Series(history.history['loss'])
     .plot(style='k', alpha=0.50, title='Loss by Epoch',
           ax=ax[0], label='loss'))
    (pd.Series(history.history['val_loss'])
     .plot(style='k', ax=ax[0], label='val_loss'))
    ax[0].legend()
    predicted = model.predict(x_test)
    pd.Series(y_test.reshape(-1),
              index=index).plot(style='k--', alpha=0.5, ax=ax[1],
                                title='Forecast vs Actual',
                                label='actual')
    pd.Series(predicted.reshape(-1),
              index=index).plot(
        style='k', label='Forecast', ax=ax[1])
    fig.tight_layout()
    ax[1].legend();
    plt.show()


def plot_forecast_3(model, x_test, y_test, index, history):
    plt.figure(figsize=(20, 10))
    ax1 = plt.subplot2grid((2, 2), (0, 0))
    pd.Series(history.history['root_mean_squared_error']).plot(style='k',
                                                               alpha=0.50,
                                                               ax=ax1,
                                                               title='RMSE by EPOCH',
                                                               label='rmse')
    pd.Series(history.history['val_root_mean_squared_error']).plot(style='k',
                                                                   ax=ax1,
                                                                   label='val_rmse')
    plt.legend()

    ax2 = plt.subplot2grid((2, 2), (0, 1))
    pd.Series(history.history['mean_absolute_error']).plot(style='k',
                                                           alpha=0.50,
                                                           ax=ax2,
                                                           title='MAE by EPOCH',
                                                           label='mae')
    pd.Series(history.history['val_mean_absolute_error']).plot(style='k',
                                                               ax=ax2,
                                                               label='val_mae')
    plt.legend()
    ax3 = plt.subplot2grid((2, 2), (1, 0), colspan=2)
    predicted = model.predict(x_test)
    pd.Series(y_test.reshape(-1),
              index=index).plot(style='k--', alpha=0.5, ax=ax3,
                                title='Forecast vs Actual',
                                label='actual')
    pd.Series(predicted.reshape(-1),
              index=index).plot(style='k', label='Forecast', ax=ax3)
    plt.legend();
    plt.show()


from keras.api.backend import clear_session

clear_session()

print(f"{x_train_Symbol.shape[2]=}")

model_a_lstm = create_model(train=x_train_Symbol, units=32)
model_a_lstm.summary()

history_a_lstm = train_model_ts(model_a_lstm, x_train_Symbol, y_train_Symbol, x_val_Symbol, y_val_Symbol)

model_a_lstm.evaluate(x=x_test_Symbol, y=y_test_Symbol)

plot_forecast(model_a_lstm, x_test_Symbol, y_test_Symbol, test_Symbol.index, history_a_lstm)

plot_forecast_3(model_a_lstm, x_test_Symbol, y_test_Symbol, test_Symbol.index, history_a_lstm)

df_tomorrow_trns_rsh = df_tomorrow_trns.drop(columns=['y']).values.reshape(3, 10, 1)

pred_tomorrow = model_a_lstm.predict(df_tomorrow_trns_rsh).reshape(-1)
df_tomorrow_trns_pred = df_tomorrow_trns
df_tomorrow_trns_pred['y'] = pred_tomorrow
model_a_lstm_pred = (df_tomorrow_trns_pred * df_tomorrow.std()) + df_tomorrow.mean()
print("Prediction : ", model_a_lstm_pred['y'].iloc[0])
print("Real Price : ", float(Symbol_LastCandle.iloc[-1]))

best_model.loc[len(best_model.index)] = ["LSTM", model_a_lstm_pred['y'].iloc[0]]

Symbol_pt_lstm, history_Symbol_pt_lstm = train_model_pt('LSTM', **params_Symbol_pt)

df_tomorrow_trns_rsh_torch = torch.from_numpy(df_tomorrow_trns_rsh.reshape(3, 10, 1)).float()

Symbol_pt_lstm.eval()
with torch.no_grad():
    h0 = Symbol_pt_lstm.init_hidden()
    y_tomorrow = Symbol_pt_lstm(df_tomorrow_trns_rsh_torch, h0)
y_tomorrow, _ = y_tomorrow

df_tomorrow_trns_pred = df_tomorrow_trns
df_tomorrow_trns_pred['y'] = y_tomorrow.reshape(-1)
Symbol_pt_lstm_pred = (df_tomorrow_trns_pred * df_tomorrow.std()) + df_tomorrow.mean()
print("Prediction : ", Symbol_pt_lstm_pred['y'].iloc[0])
print("Real Price : ", float(Symbol_LastCandle.iloc[-1]))

best_model.loc[len(best_model.index)] = ["LSTM_pytorch", Symbol_pt_lstm_pred['y'].iloc[0]]

cm = sns.color_palette("blend:red,green", as_cmap=True)
best_model.sort_values('Prediction', ascending=False).style.background_gradient(cmap=cm, axis=None)
