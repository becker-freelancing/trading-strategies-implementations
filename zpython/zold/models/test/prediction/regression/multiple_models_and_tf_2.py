import random

import numpy as np
import pandas as pd
from keras.src.losses import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, SGDRegressor, Ridge
from sklearn.metrics import root_mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from zpython.preprocessing.classification.classification_preparation_2 import prepare_data
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair


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


def regression(X_train, Y_train, X_pred, regressor):
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_scaled_train = scaler.transform(X_train)
    X_scaled_pred = scaler.transform(X_pred)

    regressor.fit(X_scaled_train, Y_train)
    train_predictions = regressor.predict(X_scaled_train)
    predictions = regressor.predict(X_scaled_pred)

    return train_predictions, predictions


def slice_data(df, split_idx, train_length, pred_length):
    data_pred_x = df.iloc[split_idx - pred_length:split_idx]
    data_pred_y = df.iloc[split_idx:split_idx + pred_length]
    data_train_x = df.iloc[split_idx - train_length - train_length:split_idx - train_length]
    data_train_y = df.iloc[split_idx - train_length:split_idx]
    return (data_train_x.drop("close", axis="columns").drop("closeTime", axis="columns"),
            data_train_y.close,
            data_pred_x.drop("close", axis="columns").drop("closeTime", axis="columns"),
            data_pred_y.close)


def calc_errors(Y_train, Y_train_actual, Y_test, Y_test_actual):
    rmse_train = root_mean_squared_error(Y_train, Y_train_actual)
    mae_train = mean_absolute_error(Y_train, Y_train_actual)
    r2_train = r2_score(Y_train, Y_train_actual)
    rmse_test = root_mean_squared_error(Y_test, Y_test_actual)
    mae_test = mean_absolute_error(Y_test, Y_test_actual)
    r2_test = r2_score(Y_test, Y_test_actual)

    return {
        "RMSE_TRAIN": rmse_train,
        "MAE_TRAIN": mae_train,
        "R2_TRAIN": r2_train,
        "RMSE_TEST": rmse_test,
        "MAE_TEST": mae_test,
        "R2_TEST": r2_test
    }


def test_model(model_name, model, data, timeframe, input_length, test_length, split_idx):
    X_train, Y_train, X_pred, Y_pred = slice_data(data, split_idx, input_length, test_length)
    y_train_actual, y_test_actual = regression(X_train, Y_train, X_pred, model)
    errors = calc_errors(Y_train, y_train_actual, Y_pred, y_test_actual)

    errors["Model"] = model_name
    errors["InputLength"] = input_length
    errors["TestLength"] = test_length
    errors["TimeFrame"] = timeframe

    return errors


if __name__ == "__main__":
    errors = pd.DataFrame(
        columns=["Model", "InputLength", "TestLength", "TimeFrame", "RMSE_TRAIN", "MAE_TRAIN", "R2_TRAIN", "RMSE_TEST",
                 "MAE_TEST", "R2_TEST"])

    time_frames = [Pair.EURUSD_1_2024, Pair.EURUSD_5_2024, Pair.EURUSD_15_2024, Pair.EURUSD_30_2024,
                   Pair.EURUSD_60_2024, Pair.EURUSD_1440]
    train_lengths = np.arange(start=5, stop=1000, step=20)
    models = [LinearRegression(), SGDRegressor(), SVR(), RandomForestRegressor(), Ridge()]
    model_names = ["lin_reg", "sgd", "svr", "random_forest", "ridge"]
    num_of_tests_per_model = 3

    total_iterations = len(time_frames) * len(train_lengths) * len(models) * num_of_tests_per_model
    current_iteration = 0

    for time_frame in time_frames:
        df = prepare_data(DataSource.HIST_DATA,
                          time_frame,
                          10,
                          30,
                          1,
                          100_000)

        all_data = generate_features(df)
        all_data = all_data.reset_index(drop=True)
        test_length = 180

        for train_length in train_lengths:

            for model, name in zip(models, model_names):

                for _ in range(num_of_tests_per_model):
                    current_iteration += 1
                    print(f"==========  {current_iteration} / {total_iterations}")

                    split_idx = random.randint(train_length + train_length + 10, len(all_data) - test_length - 10)
                    try:
                        new_errors_map = test_model(name, model, all_data, time_frame.minutes(), train_length,
                                                    test_length, split_idx)
                        new_errors = pd.DataFrame(new_errors_map, index=[current_iteration])

                        errors = pd.concat([errors, new_errors], ignore_index=True)
                    except Exception as e:
                        print(e)

    # errors.to_csv("./errors_2.csv", index=False)
