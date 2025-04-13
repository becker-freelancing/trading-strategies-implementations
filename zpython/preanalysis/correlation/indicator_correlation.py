import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_ta as ta
from scipy.stats import spearmanr

from zpython.util.data_split import analysis_data

df = analysis_data()

print(df.head())
print(df.describe())


def split_on_gaps(data):
    time_diffs = data["closeTime"].diff().dt.total_seconds()
    start_idx = 0
    dfs = []
    for i in range(1, len(data)):
        if time_diffs.iloc[i] > 60:
            dfs.append(data.iloc[start_idx:i])
            start_idx = i
    dfs.append(data.iloc[start_idx:])
    return dfs


splited = split_on_gaps(df)

outlier_cutoff = 0.01


def add_returns(data, lags_to_add):
    for lag in lags_to_add:
        data[f'return_{lag}m'] = (data["closeBid"]
                                  .pct_change(lag)
                                  .pipe(lambda x: x.clip(lower=x.quantile(outlier_cutoff),
                                                         upper=x.quantile(1 - outlier_cutoff)))
                                  .add(1)
                                  .pow(1 / lag)
                                  .sub(1)
                                  )
    return data


lags = [1, 2, 3, 6, 9, 12]
splited = [add_returns(data, lags) for data in splited]


def add_indicators(data):
    data["ATR_14"] = ta.atr(data["highBid"], data["highBid"], data["closeBid"], 14)
    data["ATR_5"] = ta.atr(data["highBid"], data["highBid"], data["closeBid"], 5)
    data["ATR_7"] = ta.atr(data["highBid"], data["highBid"], data["closeBid"], 7)
    data["ATR_10"] = ta.atr(data["highBid"], data["highBid"], data["closeBid"], 10)
    data["ATR_18"] = ta.atr(data["highBid"], data["highBid"], data["closeBid"], 18)

    data["EMA_20"] = ta.ema(data["closeBid"], length=20)
    data["EMA_10"] = ta.ema(data["closeBid"], length=10)
    data["EMA_5"] = ta.ema(data["closeBid"], length=5)
    data["EMA_30"] = ta.ema(data["closeBid"], length=30)

    data["RSI_14"] = ta.rsi(data["closeBid"], length=14)
    data["RSI_7"] = ta.rsi(data["closeBid"], length=7)
    data["RSI_20"] = ta.rsi(data["closeBid"], length=20)

    macd = ta.macd(data['closeBid'], fast=12, slow=26, signal=9)
    data['MACD_12_26_9'] = macd["MACD_12_26_9"]
    data['MACD_Signal_12_26_9'] = macd["MACDs_12_26_9"]

    bb = ta.bbands(data['closeBid'], 20)
    data['BB_Upper_20'] = bb["BBU_20_2.0"]
    data['BB_Middle_20'] = bb["BBM_20_2.0"]
    data['BB_Lower_20'] = bb["BBL_20_2.0"]

    bb = ta.bbands(data['closeBid'], 15)
    data['BB_Upper_15'] = bb["BBU_15_2.0"]
    data['BB_Middle_15'] = bb["BBM_15_2.0"]
    data['BB_Lower_15'] = bb["BBL_15_2.0"]

    bb = ta.bbands(data['closeBid'], 25)
    data['BB_Upper_25'] = bb["BBU_25_2.0"]
    data['BB_Middle_25'] = bb["BBM_25_2.0"]
    data['BB_Lower_25'] = bb["BBL_25_2.0"]

    for lag in lags:
        if lag == 1:
            continue
        data[f"momentum_{lag}"] = data[f"return_{lag}m"] - data["return_1m"]

    for t in range(1, 7):
        data[f'return_1m_t-{t}'] = data["return_1m"].shift(t)

    return data


splited = [add_indicators(data) for data in splited]


def concat(dfs):
    return pd.concat(dfs)


df = concat(splited)
exclude_columns = ["lowBid", "lowAsk", "highBid", "highAsk", "openBid", "openAsk", "closeAsk"]
df = df.drop(columns=exclude_columns)


def extract_offset(col):
    match = re.search(r't([+-])(\d+)', col)
    if match:
        sign = -1 if match.group(1) == '-' else 1
        return sign * int(match.group(2))
    else:
        return 0


def calc_correlation(data):
    corr_matrix_sub = pd.DataFrame(index=data.columns, columns=data.columns)
    pval_matrix_sub = pd.DataFrame(index=data.columns, columns=data.columns)
    corr_matrix = pd.DataFrame(index=data.columns, columns=data.columns)
    pval_matrix = pd.DataFrame(index=data.columns, columns=data.columns)
    for col1 in data.columns:
        for col2 in data.columns:
            subset = data.sample(n=5000, random_state=42)
            corr, p = spearmanr(subset[col1], subset[col2])
            corr_matrix_sub.loc[col1, col2] = corr
            pval_matrix_sub.loc[col1, col2] = p
            corr, p = spearmanr(data[col1], data[col2])
            corr_matrix.loc[col1, col2] = corr
            pval_matrix.loc[col1, col2] = p
    corr_matrix_sub = corr_matrix_sub.astype(float)
    pval_matrix_sub = pval_matrix_sub.astype(float)
    corr_matrix = corr_matrix.astype(float)
    pval_matrix = pval_matrix.astype(float)

    sorted_index = sorted(corr_matrix_sub.index, key=extract_offset)

    return (corr_matrix_sub.loc[sorted_index, sorted_index],
            pval_matrix_sub.loc[sorted_index, sorted_index],
            corr_matrix.loc[sorted_index, sorted_index],
            pval_matrix.loc[sorted_index, sorted_index])


for column in df.columns:
    if "Time" in column:
        continue
    corr_columns = []
    for lag in [0, 1, 2, 5, 10, 15, 20, 30]:
        if lag != 0:
            name = f"{column}_t+{lag}"
            df[name] = df[column].shift(lag)
            corr_columns.append(name)
        name_2 = f"{column}_t-{lag}"
        df[name_2] = df[column].shift(-lag)
        corr_columns.append(name_2)

    corr_df = df[corr_columns]
    corr_df = corr_df.dropna()
    corr_sub, pval_sub, corr, pval = calc_correlation(corr_df)

    heatmaps = [
        (corr_sub, f"Spearman-Correlation {corr_columns[0]} (Sub)"),
        (pval_sub, f"p-Wert (Spearman) {corr_columns[0]} (Sub)"),
        (corr, f"Spearman-Correlation {corr_columns[0]}"),
        (pval, f"p-Wert (Spearman) {corr_columns[0]}")
    ]

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    for ax, (data, title) in zip(axs.flat, heatmaps):
        im = ax.imshow(data, cmap='viridis', interpolation='nearest')
        ax.set_title(title)
        fig.colorbar(im, ax=ax)
        names = data.columns
        ax.set_xticks(np.arange(len(names)))
        ax.set_yticks(np.arange(len(names)))

        ax.set_xticklabels(names)
        ax.set_yticklabels(names)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    plt.tight_layout()
    plt.show()
