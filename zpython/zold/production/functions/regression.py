from japy.japy_function import japy_function
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


def slice_data(df, train_length, pred_length):
    split_idx = len(df)
    data_pred_x = df.loc[split_idx - pred_length + 1:split_idx]
    data_train_x = df.loc[split_idx - train_length - train_length + 1:split_idx - train_length]
    data_train_y = df.loc[split_idx - train_length + 1:split_idx]
    return (data_train_x.drop("close", axis="columns").drop("closeTime", axis="columns"),
            data_train_y.close,
            data_pred_x.drop("close", axis="columns").drop("closeTime", axis="columns"))


def regression(X_train, Y_train, X_pred, regressor):
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_scaled_train = scaler.transform(X_train)
    X_scaled_pred = scaler.transform(X_pred)

    regressor.fit(X_scaled_train, Y_train)
    predictions = regressor.predict(X_scaled_pred)

    return predictions


@japy_function
def random_forest_prediction(data, train_length, pred_length):
    df = data
    X_train, Y_train, X_pred = slice_data(df, train_length, pred_length)
    regressor = RandomForestRegressor()
    prediction = regression(X_train, Y_train, X_pred, regressor)
    return list(prediction)
