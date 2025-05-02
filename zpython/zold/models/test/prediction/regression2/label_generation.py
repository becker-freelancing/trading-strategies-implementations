import functools
import os.path
from concurrent.futures.thread import ThreadPoolExecutor

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, log_loss
from zpython.models.test.prediction.regression2.data_preparation import read_data_and_generate_features_without_labels
from zpython.models.test.prediction.regression2.regression_util import slice_data_without_expected, regression
from zpython.models.test.prediction.regression2.regressors import all_names, all, all_best_parameters
from zpython.util.pair import Pair

from zpython.util.path_util import from_relative_path_from_models_dir


def handle_buy(predictions, limit_buy_idx, stop_buy):
    lt_stop_buy = np.where(predictions < stop_buy)[0]
    if len(lt_stop_buy) == 0:
        return 1, 0, 0

    stop_buy_idx = lt_stop_buy[0]

    if stop_buy_idx < limit_buy_idx:
        return 0, 0, 1

    return 1, 0, 0


def handle_sell(predictions, limit_sell_idx, stop_sell):
    gt_stop_sell = np.where(predictions > stop_sell)[0]
    if len(gt_stop_sell) == 0:
        return 0, 1, 0

    stop_sell_idx = gt_stop_sell[0]

    if stop_sell_idx < limit_sell_idx:
        return 0, 0, 1

    return 0, 1, 0


def handle_none():
    return 0, 0, 1


def return_result(time, result):
    return time, result[0], result[1], result[2]


def create_actual_one(df, split_idx, stop_distance, limit_distance, model, train_length, pred_length):
    current_close = df.loc[split_idx]["close"]
    X_train, Y_train, X_pred = slice_data(df, split_idx, train_length, pred_length)
    predictions = regression(X_train, Y_train, X_pred, model)
    limit_buy = current_close + limit_distance
    limit_sell = current_close - limit_distance
    stop_buy = current_close - stop_distance
    stop_sell = current_close + stop_distance
    gt_limit_buy = np.where(predictions > limit_buy)[0]
    lt_limit_sell = np.where(predictions < limit_sell)[0]
    time = df.loc[split_idx]["closeTime"]

    if len(lt_limit_sell) > 0 and len(gt_limit_buy) > 0:
        limit_sell_idx = lt_limit_sell[0]
        limit_buy_idx = gt_limit_buy[0]
        if limit_buy_idx < limit_sell_idx:
            return return_result(time, handle_buy(predictions, limit_buy_idx, stop_buy))
        else:
            return return_result(time, handle_sell(predictions, limit_sell_idx, stop_sell))

    if len(lt_limit_sell) > 0:
        limit_sell_idx = lt_limit_sell[0]
        return return_result(time, handle_sell(predictions, limit_sell_idx, stop_sell))

    if len(gt_limit_buy) > 0:
        limit_buy_idx = gt_limit_buy[0]
        return return_result(time, handle_buy(predictions, limit_buy_idx, stop_buy))

    return return_result(time, handle_none())


def create_actual(regression_df, stop_distance, limit_distance, model_supplier, train_length, pred_length):
    needed_length = train_length + train_length + pred_length
    # regression_df_grouped = [regression_df.iloc[i:i + needed_length] for i in
    #                          range(len(regression_df) - (needed_length - 1))]

    min_idx = regression_df.index.min()
    max_idx = regression_df.index.max()

    def apply(df):
        curr_idx = df.name
        if curr_idx - train_length - train_length < min_idx:
            return return_result(pd.to_datetime("2099-01-01 00:00:00"), handle_none())
        return create_actual_one(regression_df, curr_idx, stop_distance, limit_distance, model_supplier(), train_length,
                                 pred_length)

    result = regression_df.apply(lambda x: apply(x), axis=1)
    # result = [apply(df) for df in regression_df_grouped]

    parsed = result.apply(pd.Series)
    parsed.columns = ["closeTime", "ActualBuy", "ActualSell", "ActualNone"]
    return parsed


def calc_error(expected, actual):
    merge = pd.merge(expected, actual, on="closeTime", how="inner")
    act = merge[["ActualBuy", "ActualSell", "ActualNone"]].to_numpy()
    exp = merge[["BuyOutput", "SellOutput", "NoneOutput"]].to_numpy()

    accuracy = accuracy_score(exp, act)
    prec, recall, f1, _, = precision_recall_fscore_support(exp, act, average="macro")
    logloss = log_loss(exp, act)
    auc_roc = 0  # roc_auc_score(exp, act)
    kappa = 0  # cohen_kappa_score(exp, act)

    total_len_exp = len(merge)
    buy_len_exp = len(merge[merge["BuyOutput"] == 1])
    sell_len_exp = len(merge[merge["SellOutput"] == 1])
    none_len_exp = len(merge[merge["NoneOutput"] == 1])
    buy_len_act = len(merge[merge["ActualBuy"] == 1])
    sell_len_act = len(merge[merge["ActualSell"] == 1])
    none_len_act = len(merge[merge["ActualNone"] == 1])

    return {
        "Accuracy": accuracy,
        "Precision": prec,
        "Recall": recall,
        "F1": f1,
        "LogLoss": logloss,
        "AUC_ROC": auc_roc,
        "Kappa": kappa,
        "ActualNoneRatio": none_len_act / total_len_exp,
        "ActualBuyRatio": buy_len_act / total_len_exp,
        "ActualSellRatio": sell_len_act / total_len_exp,
        "ExpectedNoneRatio": none_len_exp / total_len_exp,
        "ExpectedBuyRatio": buy_len_exp / total_len_exp,
        "ExpectedSellRatio": sell_len_exp / total_len_exp
    }


def execute_for_parameter(df, stop_in_euro, limit_in_euro, size, model_supplier, train_length, pred_length):
    df = add_outputs(df, stop_in_euro, limit_in_euro, size)
    regression_df = generate_features(df)

    stop_distance = stop_in_euro / 100_000 / size
    limit_distance = limit_in_euro / 100_000 / size

    actual = create_actual(regression_df, stop_distance, limit_distance, model_supplier, train_length, pred_length)
    expected = df[["closeTime", "BuyOutput", "SellOutput", "NoneOutput"]]
    err = calc_error(expected, actual)
    return err


def execute_prediction(close_time, X_train, Y_train, X_pred, regressor):
    prediction = regression(X_train, Y_train, X_pred, regressor())
    return pd.DataFrame(data={
        "closeTime": close_time,
        "prediction": prediction
    })


def execute_for_regressor(df, train_length, pred_length, regressor):
    X_trains = [df.iloc[i - train_length - pred_length:i] for i in range(train_length + pred_length, len(df))]
    splits = [slice_data_without_expected(x_train, np.max(x_train.index), train_length, pred_length) for x_train in
              X_trains]
    fixed_execute_prediction = functools.partial(execute_prediction, regressor=regressor)
    with ThreadPoolExecutor(max_workers=400) as executor:
        predictions = executor.map(lambda split: fixed_execute_prediction(close_time=split[3],
                                                                          X_train=split[0],
                                                                          Y_train=split[1],
                                                                          X_pred=split[2]),
                                   splits)

        prediction = pd.DataFrame(columns=["closeTime", "prediction"])

        for pred in predictions:
            prediction = pd.concat([prediction, pred], ignore_index=True)

        return prediction


if __name__ == "__main__":
    time_frames = [Pair.EURUSD_1_2024, Pair.EURUSD_5_2024, Pair.EURUSD_15_2024, Pair.EURUSD_30_2024,
                   Pair.EURUSD_60_2024, Pair.EURUSD_1440]
    pred_length = 180

    regressors = all()
    regressor_names = all_names()
    best_parameters = all_best_parameters()

    curr_iteration = 0
    num_iterations = len(time_frames) * len(regressors)

    for time_frame in time_frames:

        df = read_data_and_generate_features_without_labels(time_frame)

        for regressor_name, regressor, parameters in zip(regressor_names, regressors, best_parameters):
            curr_iteration += 1
            train_length = parameters
            print(f"{curr_iteration} / {num_iterations}")
            prediction_for_time = execute_for_regressor(df, train_length, pred_length, regressor_name, regressor)

            path = from_relative_path_from_models_dir(f"{regressor_name}")
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=False)
            path = f"{path}/prediction_M{time_frame.minutes()}_train_{train_length}.csv"
            prediction_for_time.to_csv(path, index=False)
