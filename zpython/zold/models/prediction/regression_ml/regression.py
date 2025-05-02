import os

import pandas as pd
from zpython.models.test.prediction.regression.backtest import lin_reg_meta_data_supplier, rand_for_meta_data_supplier, \
    ridge_meta_data_supplier, sgd_meta_data_supplier, svr_meta_data_supplier
from zpython.models.test.prediction.regression.backtest import lin_reg_supplier, rand_for_supplier, ridge_supplier, \
    sgd_supplier, svr_supplier, slice_data, regression
from zpython.models.test.prediction.regression.multiple_models_and_tf_2 import generate_features
from zpython.util.hist_data_data_reader import read_data

best_models = pd.read_csv(
    "C:/Users/jasb/Documents/Ausbildung/Bachelor/trading-strategies-implementations/zpython/models/test/prediction/regression/backtest_results_ratios_best.csv")


def get_model(name):
    if name == "rand_for":
        return rand_for_supplier
    if name == "sgd":
        return sgd_supplier
    if name == "svr":
        return svr_supplier
    if name == "lin_reg":
        return lin_reg_supplier
    if name == "ridge":
        return ridge_supplier


def get_metadata(name):
    if name == "rand_for":
        return rand_for_meta_data_supplier()
    if name == "sgd":
        return sgd_meta_data_supplier()
    if name == "svr":
        return svr_meta_data_supplier()
    if name == "lin_reg":
        return lin_reg_meta_data_supplier()
    if name == "ridge":
        return ridge_meta_data_supplier()


def create_actual_one(df, split_idx, model, train_length, pred_length):
    try:
        X_train, Y_train, X_pred = slice_data(df, split_idx, train_length, pred_length)
        predictions = regression(X_train, Y_train, X_pred, model)
        return predictions
    except Exception:
        return None


def create_actual(regression_df, model_supplier, train_length, pred_length):
    min_idx = regression_df.index.min()

    def apply(df):
        curr_idx = df.name
        if curr_idx - train_length - train_length < min_idx:
            return df["closeTime"], None
        return df["closeTime"], create_actual_one(regression_df, curr_idx, model_supplier(), train_length,
                                                  pred_length)

    result = regression_df.apply(apply, axis=1)
    # result = [apply(df) for df in regression_df_grouped]

    parsed = pd.DataFrame(result.tolist(), columns=['closeTime', 'prediction'])
    return parsed.dropna()


df = read_data("EURUSD_1_2024.csv.zip")
df.reset_index(inplace=True)
df = generate_features(df)
df = df[df["closeTime"] < pd.to_datetime("2023-03-01 00:00:00")]

for model_name in ["svr", "ridge", "sgd", "rand_for"]:
    print(model_name)
    name, train_length, pred_length = get_metadata(model_name)
    model = get_model(model_name)

    actual = create_actual(df, model, train_length, pred_length)

    path = f"C:/Users/jasb/AppData/Roaming/krypto-java/models/HIST_DATA/EURUSD_1/{model_name}/"
    if not os.path.exists(path):
        os.makedirs(path)
    # actual.to_csv(f"{path}train_{train_length}_pred{pred_length}.csv.zip", compression="zip", index=False)
