import functools
from concurrent.futures.thread import ThreadPoolExecutor
from itertools import product

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, log_loss

from zpython.models.test.prediction.regression2.data_preparation import generate_features
from zpython.models.test.prediction.regression2.regression_util import slice_data, regression
from zpython.models.test.prediction.regression2.regressors import all, all_best_parameters, all_names
from zpython.preprocessing.classification.classification_preparation_2 import add_outputs, read_data_for_preparation
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair


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
    X_train, Y_train, X_pred, close_time = slice_data(df, split_idx, train_length, pred_length)
    predictions = regression(X_train, Y_train, X_pred, model)[1]
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


def execute_for_parameter(df, stop_in_euro, limit_in_euro, size, model_supplier, train_length, pred_length, model_name):
    df = add_outputs(df, stop_in_euro, limit_in_euro, size)
    regression_df = generate_features(df)

    stop_distance = stop_in_euro / 100_000 / size
    limit_distance = limit_in_euro / 100_000 / size

    actual = create_actual(regression_df, stop_distance, limit_distance, model_supplier, train_length, pred_length)
    expected = df[["closeTime", "BuyOutput", "SellOutput", "NoneOutput"]]
    err = calc_error(expected, actual)
    err["Model"] = model_name
    return err


def find_parameter_tuples(regressors, regresssor_names, executed_tests, time_frame):
    tuples = []
    for i in range(len(regressors)):
        regressor = regressors[i]
        name = regresssor_names[i]
        sliced = executed_tests[
            (executed_tests["Model"] == name) & (executed_tests["TimeFrame"] == time_frame.minutes())]
        min_row = sliced.loc[sliced['RMSE_TEST'].idxmin()]
        tuples.append((name, regressor, min_row["InputLength"], 180))

    return tuples


def execute_for_regressor():
    pass


def permutate(stops, limits, sizes, parameter_tuples):
    perm = list(product(stops, limits, sizes, parameter_tuples))
    return perm


def execute_for_regressors(df, errors, executed_tests, time_frame, regresssor_names, regressors, stops, limits, sizes):
    parameter_tuples = find_parameter_tuples(regressors, regresssor_names, executed_tests, time_frame)

    fixed_execute_for_parameter = functools.partial(execute_for_parameter, df=df)

    permutations = permutate(stops, limits, sizes, parameter_tuples)
    with ThreadPoolExecutor(max_workers=1000) as executor:
        curr_errors = executor.map(lambda perm: fixed_execute_for_parameter(stop_in_euro=perm[0],
                                                                            limit_in_euro=perm[1],
                                                                            size=perm[2],
                                                                            model_name=perm[3][0],
                                                                            model_supplier=perm[3][1],
                                                                            train_length=perm[3][2],
                                                                            pred_length=perm[3][3]),
                                   permutations)

        for curr_error in curr_errors:
            curr_error["TimeFrame"] = time_frame.minutes()
            errors = pd.concat([errors, curr_errors], ignore_index=True)

    return errors


if __name__ == "__main__":
    errors = pd.DataFrame(
        columns=["Model", "Stop", "Limit", "Size", "TimeFrame", "ActualNoneRatio", "ActualBuyRatio", "ActualSellRatio",
                 "ExpectedNoneRatio", "ExpectedBuyRatio", "ExpectedSellRatio"
                                                          "Accuracy", "Precision", "Recall", "F1", "LogLoss", "AUC_ROC",
                 "Kappa"])
    idx = 0
    time_frames = [Pair.EURUSD_1_2024, Pair.EURUSD_5_2024, Pair.EURUSD_15_2024, Pair.EURUSD_30_2024,
                   Pair.EURUSD_60_2024, Pair.EURUSD_1440]
    executed_tests = pd.read_csv("./regressors_for_tf_test.csv")

    regressors = all()
    regresssor_names = all_names()
    stops = [10, 20, 30, 50, 70, 100]
    limits = [10, 20, 30, 50, 100, 200]
    sizes = [0.2, 0.5, 1]
    metadata_supplier = all_best_parameters()

    iterations = len(regressors) * len(stops) * len(limits) * len(sizes)

    try:
        for time_frame in time_frames:
            df = read_data_for_preparation(DataSource.HIST_DATA, time_frame, 3000)
            errors = execute_for_regressors(df, errors, executed_tests, time_frame, regresssor_names, regressors, stops,
                                            limits, sizes)

            errors.to_csv("./backtest_results_ratios.csv", index=False)
    except Exception as e:
        errors.to_csv("./backtest_results_ratios.csv", index=False)
        raise e
