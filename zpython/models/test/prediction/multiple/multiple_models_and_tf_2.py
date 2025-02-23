import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, SGDRegressor, Ridge
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR


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
    df_new = df_new.dropna(axis=0)
    return df_new


errors = pd.DataFrame(columns=["Model", "InputLength", "TestLength", "TimeFrame", "RMSE", "MAE", "R2"])

time_frames = [1, 5, 15, 30, 60, 1440]
train_lengths = np.arange(start=1, stop=1000, step=20)
models = [LinearRegression(), SGDRegressor(), SVR(), RandomForestRegressor(), Ridge()]
model_names = ["lin_reg", "sgd", "svr", "random_forest", "ridge"]
number_of_predictions = 10

total_iterations = len(time_frames) * len(train_lengths) * len(models) * number_of_predictions
current_iteration = 0

for time_frame in time_frames:
    if time_frame == 1440:
        df = pd.read_csv(f"C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_{time_frame}.csv.zip",
                         compression="zip")
    else:
        df = pd.read_csv(f"C:/Users/jasb/AppData/Roaming/krypto-java/data-histdata/EURUSD_{time_frame}_2024.csv.zip",
                         compression="zip")
    df.set_index("closeTime", inplace=True)
    all_data = generate_features(df)
    test_length = 180
    data_test = all_data.iloc[len(all_data) - test_length:]
    X_test = data_test.drop('close', axis='columns')
    y_test = data_test.close

    for train_length in train_lengths:
        data_train = all_data.iloc[len(all_data) - test_length - train_length:len(all_data) - test_length]
        X_train = data_train.drop('close', axis='columns')
        y_train = data_train.close

        scaler = StandardScaler()
        scaler.fit(X_train)
        X_scaled_train = scaler.transform(X_train)
        X_scaled_test = scaler.transform(X_test)

        for model, name in zip(models, model_names):
            current_iteration += 1
            print(f"==========  {current_iteration} / {total_iterations}")
            model.fit(X_scaled_train, y_train)
            predictions = model.predict(X_scaled_test)

            rmse = root_mean_squared_error(y_test, predictions)
            print('RMSE: {0:.3f}'.format(rmse))
            mae = mean_absolute_error(y_test, predictions)
            print('MAE: {0:.3f}'.format(mae))
            r2 = r2_score(y_test, predictions)
            print('R^2: {0:.3f}'.format(r2))

            new_errors = pd.DataFrame({
                "Model": name,
                "InputLength": len(data_train),
                "TestLength": len(data_test),
                "TimeFrame": time_frame,
                "RMSE": rmse,
                "MAE": mae,
                "R2": r2
            }, index=[current_iteration])

            errors = pd.concat([errors, new_errors], ignore_index=True)

errors.to_csv("./errors_2.csv", index=False)
