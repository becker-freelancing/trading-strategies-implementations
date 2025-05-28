import itertools
import warnings

import numpy as np
import pandas as pd
import pandas_ta as ta
import tqdm

from zpython.util import split_on_gaps
from zpython.util.data_split import train_data
from zpython.util.market_regime import MarketRegimeDetector


class DataCache:
    indicators_cache = {}

def _add_returns(data,
                 lags_to_add,
                 column_name,
                 outlier_cutoff=0.01):
    for lag in lags_to_add:
        data.loc[:, f'logReturn_{column_name}_{lag}min'] = np.log(data[column_name] / data[column_name].shift(lag)) \
            .pipe(lambda x: x.clip(lower=x.quantile(outlier_cutoff),
                                   upper=x.quantile(1 - outlier_cutoff)))
    return data


def _create_long_indicators_for_part(data, close_column, momentum_lags):
    for lag in momentum_lags:
        data.loc[:, f'return_{close_column}_{lag}min'] = (data["closeBid"] - data["closeBid"].shift(lag)) / data[
            "closeBid"].shift(lag)

    for length in [5, 10, 20, 30]:
        data.loc[:, f"Std_{length}"] = ta.stdev(data["logReturn_closeBid_1min"], length=length)

    data.loc[:, "SMA_20"] = ta.sma(data["logReturn_closeBid_1min"], length=20)
    data.loc[:, "SMA_10"] = ta.sma(data["logReturn_closeBid_1min"], length=10)
    data.loc[:, "SMA_5"] = ta.sma(data["logReturn_closeBid_1min"], length=5)
    data.loc[:, "SMA_30"] = ta.sma(data["logReturn_closeBid_1min"], length=30)

    macd_fast = [5, 12, 28, 24]
    macd_slow = [9, 18, 26, 45, 50]
    macd_signal = [5, 9, 15, 20]
    for fast, slow, signal in list(itertools.product(macd_fast, macd_slow, macd_signal)):
        if fast > slow:
            continue
        macd = ta.macd(data["logReturn_closeBid_1min"], fast=fast, slow=slow, signal=signal)
        name = f"MACD_{fast}_{slow}_{signal}"
        data.loc[:, name] = macd[name]
        data.loc[:, f"MACD_Signal_{fast}_{slow}_{signal}"] = macd[f"MACDs_{fast}_{slow}_{signal}"]

    for length in [12, 20, 50, 100]:
        data.loc[:, f"ROC_{length}"] = ta.roc(data["logReturn_closeBid_1min"], length=length)

    for length in [7, 10, 14, 20, 30]:
        data.loc[:, f"ADX_{length}"] = ta.adx(data["logReturn_highBid_1min"], data["logReturn_lowBid_1min"],
                                              data["logReturn_closeBid_1min"], length=length)[f"ADX_{length}"]

    for length in [5, 7, 20, 30]:
        data.loc[:, f"HistVola_{length}"] = data["logReturn_closeBid_1min"].rolling(length).std()

    for length in [5, 10, 20, 30]:
        data.loc[:, f"ZScore_{length}"] = (data["logReturn_closeBid_1min"] - data[f"SMA_{length}"]) / data[
            f"Std_{length}"]

    # Cross Features
    for rsi, fast, slow, signal in itertools.product([7, 14, 20], macd_fast, macd_slow, macd_signal):
        if fast > slow:
            continue
        data.loc[:, f"RSI_{rsi}_MACD_{fast}_{slow}_{signal}"] = data[f"RSI_{rsi}"] * data[
            f"MACD_{fast}_{slow}_{signal}"]

    for ema in [5, 10, 20, 30]:
        data.loc[:, f"EMA_{ema}_Less_logReturn_closeBid_1min"] = (
                    data[f"EMA_{ema}"] < data["logReturn_closeBid_1min"]).astype(int)

    for rsi in [7, 14, 20]:
        data.loc[:, f"RSI_{rsi}_Greater_70"] = (data[f"RSI_{rsi}"] > 70).astype(int)
        data.loc[:, f"RSI_{rsi}_Less_30"] = (data[f"RSI_{rsi}"] < 30).astype(int)
        for vola in [5, 7, 20, 30]:
            data.loc[:, f"RSI_{rsi}_Vola_{vola}"] = data[f"RSI_{rsi}"] * data[f"HistVola_{vola}"]

    for volume in [5, 10, 20, 30, 50]:
        data.loc[:, f"VolumeSpike_{volume}"] = (data["volume"].rolling(volume).mean() * 1.5 < data["volume"]).astype(
            int)

    return data


def _create_indicator_for_part(data,
                               close_column,
                               momentum_lags,
                               long=False):
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
    data.loc[:, "EMA_50"] = ta.ema(data["logReturn_closeBid_1min"], length=50)
    data.loc[:, "EMA_200"] = ta.ema(data["logReturn_closeBid_1min"], length=200)

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

    if long:
        data = data.dropna()
        data = _create_long_indicators_for_part(data, close_column, momentum_lags)

    return data


def _concat(dfs):
    return pd.concat(dfs)


def create_indicators(data_read_function=train_data,
                      close_column='closeBid',
                      high_column='highBid',
                      low_column='lowBid',
                      momentum_lags=(1, 2, 3, 6, 9, 12),
                      limit=100_000_000,
                      time_frame=1,
                      regime_detector=None):
    cache_content = DataCache.indicators_cache.get(data_read_function)
    if cache_content is not None:
        print("Using Cache Content for data")
        return cache_content, regime_detector
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        print(f"Reading data (M{time_frame})...")
        data = data_read_function(time_frame=time_frame)
        print("Creating indicators...")
        data = data.reset_index(drop=True)
        data = data.iloc[:limit]
        data = data.sort_values(by="closeTime")

        if not regime_detector:
            regime_detector = MarketRegimeDetector()
        if not regime_detector.is_fitted():
            regime_detector.fit(data, close_column, time_frame)
        data["regime"] = regime_detector.transform(data, close_column, time_frame)

        datas = split_on_gaps(data, time_frame)
        datas = [_add_returns(part, momentum_lags, low_column) for part in datas]
        datas = [_add_returns(part, momentum_lags, close_column) for part in datas]
        datas = [_add_returns(part, momentum_lags, high_column) for part in datas]

        datas = [_create_indicator_for_part(part, close_column, momentum_lags) for part in datas]

        data = _concat(datas)
        exclude_columns = ["lowBid", "lowAsk", "highBid", "highAsk", "openBid", "openAsk", "closeAsk", "closeBid"]
        data = data.drop(columns=exclude_columns)
        data.set_index("closeTime", inplace=True)
        DataCache.indicators_cache[data_read_function] = data
        return data, regime_detector


def create_multiple_indicators(data_read_function=train_data,
                               close_column='closeBid',
                               high_column='highBid',
                               low_column='lowBid',
                               momentum_lags=(1, 2, 3, 6, 9, 12),
                               limit=100_000_000,
                               time_frame=1):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        print("Reading data...")
        data = data_read_function(time_frame=time_frame)
        print("Creating indicators...")
        data = data.reset_index(drop=True)
        data = data.iloc[:limit]

        with_indicators = []
        for part in tqdm.tqdm(split_on_gaps(data, time_frame), "Creating Indicators"):
            part = _add_returns(part, momentum_lags, low_column)
            part = _add_returns(part, momentum_lags, close_column)
            part = _add_returns(part, momentum_lags, high_column)
            part = _create_indicator_for_part(part, close_column, momentum_lags, long=True)
            with_indicators.append(part)

        data = _concat(with_indicators)
        exclude_columns = ["lowBid", "lowAsk", "highBid", "highAsk", "openBid", "openAsk", "closeAsk", "closeBid"]
        data = data.drop(columns=exclude_columns)
        data.set_index("closeTime", inplace=True)
        return data
