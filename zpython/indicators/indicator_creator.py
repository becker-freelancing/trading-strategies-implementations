import warnings

import numpy as np
import pandas as pd
import pandas_ta as ta

from zpython.util.data_split import train_data


def _add_returns(data,
                 lags_to_add,
                 column_name,
                 outlier_cutoff=0.01):
    for lag in lags_to_add:
        data.loc[:, f'logReturn_{column_name}_{lag}min'] = np.log(data[column_name] / data[column_name].shift(lag)) \
            .pipe(lambda x: x.clip(lower=x.quantile(outlier_cutoff),
                                   upper=x.quantile(1 - outlier_cutoff)))
    return data


def _split_on_gaps(data):
    time_diffs = data["closeTime"].diff().dt.total_seconds()
    start_idx = 0
    dfs = []
    for i in range(1, len(data)):
        if time_diffs.iloc[i] > 60:
            dfs.append(data.iloc[start_idx:i])
            start_idx = i
    dfs.append(data.iloc[start_idx:])
    return dfs


def _create_indicator_for_part(data,
                               close_column,
                               momentum_lags):
    data.loc[:, "ATR_14"] = ta.atr(data["logReturn_highBid_1min"], data["logReturn_lowBid_1min"],
                                   data["logReturn_closeBid_1min"], 14)
    data.loc[:, "ATR_5"] = ta.atr(data["logReturn_highBid_1min"], data["logReturn_lowBid_1min"],
                                  data["logReturn_closeBid_1min"], 5)
    data.loc[:, "ATR_7"] = ta.atr(data["logReturn_highBid_1min"], data["logReturn_lowBid_1min"],
                                  data["logReturn_closeBid_1min"], 7)
    data.loc[:, "ATR_10"] = ta.atr(data["logReturn_highBid_1min"], data["logReturn_lowBid_1min"],
                                   data["logReturn_closeBid_1min"], 10)
    data.loc[:, "ATR_18"] = ta.atr(data["logReturn_highBid_1min"], data["logReturn_lowBid_1min"],
                                   data["logReturn_closeBid_1min"], 18)

    data.loc[:, "EMA_20"] = ta.ema(data["logReturn_closeBid_1min"], length=20)
    data.loc[:, "EMA_10"] = ta.ema(data["logReturn_closeBid_1min"], length=10)
    data.loc[:, "EMA_5"] = ta.ema(data["logReturn_closeBid_1min"], length=5)
    data.loc[:, "EMA_30"] = ta.ema(data["logReturn_closeBid_1min"], length=30)

    data.loc[:, "RSI_14"] = ta.rsi(data["logReturn_closeBid_1min"], length=14)
    data.loc[:, "RSI_7"] = ta.rsi(data["logReturn_closeBid_1min"], length=7)
    data.loc[:, "RSI_20"] = ta.rsi(data["logReturn_closeBid_1min"], length=20)

    macd = ta.macd(data["logReturn_closeBid_1min"], fast=12, slow=26, signal=9)
    data.loc[:, 'MACD_12_26_9'] = macd["MACD_12_26_9"]
    data.loc[:, 'MACD_Signal_12_26_9'] = macd["MACDs_12_26_9"]

    bb = ta.bbands(data["logReturn_closeBid_1min"], 20)
    data.loc[:, 'BB_Upper_20'] = bb["BBU_20_2.0"]
    data.loc[:, 'BB_Middle_20'] = bb["BBM_20_2.0"]
    data.loc[:, 'BB_Lower_20'] = bb["BBL_20_2.0"]

    bb = ta.bbands(data["logReturn_closeBid_1min"], 15)
    data.loc[:, 'BB_Upper_15'] = bb["BBU_15_2.0"]
    data.loc[:, 'BB_Middle_15'] = bb["BBM_15_2.0"]
    data.loc[:, 'BB_Lower_15'] = bb["BBL_15_2.0"]

    bb = ta.bbands(data["logReturn_closeBid_1min"], 25)
    data.loc[:, 'BB_Upper_25'] = bb["BBU_25_2.0"]
    data.loc[:, 'BB_Middle_25'] = bb["BBM_25_2.0"]
    data.loc[:, 'BB_Lower_25'] = bb["BBL_25_2.0"]

    for lag in momentum_lags:
        if lag == 1:
            continue
        data.loc[:, f"momentum_{lag}"] = data[f"logReturn_{close_column}_{lag}min"] - data["logReturn_closeBid_1min"]

    for t in range(1, 7):
        data.loc[:, f'logReturn_1m_t-{t}'] = data["logReturn_closeBid_1min"].shift(t)

    return data


def _concat(dfs):
    return pd.concat(dfs)


def create_indicators(data_read_function=train_data,
                      close_column='closeBid',
                      high_column='highBid',
                      low_column='lowBid',
                      momentum_lags=(1, 2, 3, 6, 9, 12)):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        print("Reading data...")
        data = data_read_function()
        print("Creating indicators...")
        data = data.reset_index(drop=True)

        datas = _split_on_gaps(data)
        datas = [_add_returns(part, momentum_lags, low_column) for part in datas]
        datas = [_add_returns(part, momentum_lags, close_column) for part in datas]
        datas = [_add_returns(part, momentum_lags, high_column) for part in datas]

        datas = [_create_indicator_for_part(part, close_column, momentum_lags) for part in datas]

        data = _concat(datas)
        exclude_columns = ["lowBid", "lowAsk", "highBid", "highAsk", "openBid", "openAsk", "closeAsk", "closeBid"]
        data = data.drop(columns=exclude_columns)
        data.set_index("closeTime", inplace=True)
        return data
