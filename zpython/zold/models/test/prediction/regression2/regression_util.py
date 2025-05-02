import numpy as np
from sklearn.preprocessing import StandardScaler


def slice_data(df, split_idx, train_length, pred_length):
    data_pred_x = df.iloc[split_idx - pred_length:split_idx]
    data_pred_y = df.iloc[split_idx:split_idx + pred_length]
    data_train_x = df.iloc[split_idx - train_length - train_length:split_idx - train_length]
    data_train_y = df.iloc[split_idx - train_length:split_idx]
    return (data_train_x.drop("close", axis="columns").drop("closeTime", axis="columns"),
            data_train_y.close,
            data_pred_x.drop("close", axis="columns").drop("closeTime", axis="columns"),
            data_pred_y.close)


def slice_data_without_expected(df, split_idx, train_length, pred_length):
    data_pred_x = df.iloc[split_idx - pred_length:split_idx]
    data_train_x = df.iloc[split_idx - train_length - train_length:split_idx - train_length]
    data_train_y = df.iloc[split_idx - train_length:split_idx]
    return (data_train_x.drop("close", axis="columns").drop("closeTime", axis="columns"),
            data_train_y.close,
            data_pred_x.drop("close", axis="columns").drop("closeTime", axis="columns"),
            np.max(data_pred_x["closeTime"].values))


def regression(X_train, Y_train, X_pred, regressor):
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_scaled_train = scaler.transform(X_train)
    X_scaled_pred = scaler.transform(X_pred)

    regressor.fit(X_scaled_train, Y_train)
    train_predictions = regressor.predict(X_scaled_train)
    predictions = regressor.predict(X_scaled_pred)

    return train_predictions, predictions
