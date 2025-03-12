import pandas as pd

from zpython.preprocessing.classification.classification_preparation_2 import prepare_data
from zpython.util.data_source import DataSource
from zpython.util.hist_data_data_reader import read_data


def read_data_with_labels(time_frame, stop=10, limit=30, size=1):
    return prepare_data(DataSource.HIST_DATA,
                        time_frame,
                        stop,
                        limit,
                        size,
                        100_000)


def read_and_generate_features_with_labels(time_frame, stop=10, limit=30, size=1):
    df = read_data_with_labels(time_frame, stop, limit, size)
    df = generate_features(df)
    return df


def read_data_without_labels(time_frame):
    df = read_data(DataSource.HIST_DATA.file_path(time_frame))
    return df


def read_data_and_generate_features_without_labels(time_frame):
    df = read_data_with_labels(time_frame)
    df = generate_features(df)
    return df


def generate_features(df):
    """ Generate features for a stock/index/currency/commodity based on historical price and performance
    Args:
        df (dataframe with columns "open", "close", "high", "low", "volume")
    Returns:
        dataframe, data set with new features
    """
    df_new = pd.DataFrame()

    # 6 original features
    df_new['open'] = df['openBid']
    df_new['open_1'] = df['openBid'].shift(1)
    df_new['close_1'] = df['closeBid'].shift(1)
    df_new['high_1'] = df['highBid'].shift(1)
    df_new['low_1'] = df['lowBid'].shift(1)

    # 50 original features
    # average price
    df_new['avg_price_5'] = df['closeBid'].rolling(window=5).mean().shift(1)
    df_new['avg_price_30'] = df['closeBid'].rolling(window=21).mean().shift(1)
    df_new['avg_price_90'] = df['closeBid'].rolling(window=63).mean().shift(1)
    df_new['avg_price_365'] = df['closeBid'].rolling(window=252).mean().shift(1)

    # average price ratio
    df_new['ratio_avg_price_5_30'] = df_new['avg_price_5'] / df_new['avg_price_30']
    df_new['ratio_avg_price_905_'] = df_new['avg_price_5'] / df_new['avg_price_90']
    df_new['ratio_avg_price_5_365'] = df_new['avg_price_5'] / df_new['avg_price_365']
    df_new['ratio_avg_price_30_90'] = df_new['avg_price_30'] / df_new['avg_price_90']
    df_new['ratio_avg_price_30_365'] = df_new['avg_price_30'] / df_new['avg_price_365']
    df_new['ratio_avg_price_90_365'] = df_new['avg_price_90'] / df_new['avg_price_365']

    # standard deviation of prices
    df_new['std_price_5'] = df['closeBid'].rolling(window=5).std().shift(1)
    df_new['std_price_30'] = df['closeBid'].rolling(window=21).std().shift(1)
    df_new['std_price_90'] = df['closeBid'].rolling(window=63).std().shift(1)
    df_new['std_price_365'] = df['closeBid'].rolling(window=252).std().shift(1)

    # standard deviation ratio of prices
    df_new['ratio_std_price_5_30'] = df_new['std_price_5'] / df_new['std_price_30']
    df_new['ratio_std_price_5_90'] = df_new['std_price_5'] / df_new['std_price_90']
    df_new['ratio_std_price_5_365'] = df_new['std_price_5'] / df_new['std_price_365']
    df_new['ratio_std_price_30_90'] = df_new['std_price_30'] / df_new['std_price_90']
    df_new['ratio_std_price_30_365'] = df_new['std_price_30'] / df_new['std_price_365']
    df_new['ratio_std_price_90_365'] = df_new['std_price_90'] / df_new['std_price_365']

    # return
    df_new['return_1'] = ((df['closeBid'] - df['closeBid'].shift(1)) / df['closeBid'].shift(1)).shift(1)
    df_new['return_5'] = ((df['closeBid'] - df['closeBid'].shift(5)) / df['closeBid'].shift(5)).shift(1)
    df_new['return_30'] = ((df['closeBid'] - df['closeBid'].shift(21)) / df['closeBid'].shift(21)).shift(1)
    df_new['return_90'] = ((df['closeBid'] - df['closeBid'].shift(63)) / df['closeBid'].shift(63)).shift(1)
    df_new['return_365'] = ((df['closeBid'] - df['closeBid'].shift(252)) / df['closeBid'].shift(252)).shift(1)

    # average of return
    df_new['moving_avg_5'] = df_new['return_1'].rolling(window=5).mean()
    df_new['moving_avg_30'] = df_new['return_1'].rolling(window=21).mean()
    df_new['moving_avg_30'] = df_new['return_1'].rolling(window=63).mean()
    df_new['moving_avg_365'] = df_new['return_1'].rolling(window=252).mean()

    # the target
    df_new['close'] = df['closeBid']
    df_new["closeTime"] = df["closeTime"]
    df_new = df_new.dropna(axis=0)
    return df_new
