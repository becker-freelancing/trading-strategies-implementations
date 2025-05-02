import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, log_loss
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from zpython.models.test.prediction.regression.multiple_models_and_tf_2 import generate_features
from zpython.preprocessing.classification.classification_preparation_2 import read_data_for_preparation, add_outputs
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair


def slice_data(df, split_idx, train_length, pred_length):
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


def lin_reg_supplier():
    return LinearRegression()


def lin_reg_meta_data_supplier():
    return "lin_reg", 665, 180


def rand_for_supplier():
    return RandomForestRegressor()


def rand_for_meta_data_supplier():
    return "rand_for", 485, 180


def ridge_supplier():
    return Ridge()


def ridge_meta_data_supplier():
    return "ridge", 525, 180


def sgd_supplier():
    return SVR()


def sgd_meta_data_supplier():
    return "sgd", 345, 180


def svr_supplier():
    return SVR()


def svr_meta_data_supplier():
    return "svr", 85, 180


if __name__ == "__main__":
    errors = pd.DataFrame(
        columns=["model", "stop", "limit", "size", "ActualNoneRatio", "ActualBuyRatio", "ActualSellRatio",
                 "ExpectedNoneRatio", "ExpectedBuyRatio", "ExpectedSellRatio"
                                                          "Accuracy", "Precision", "Recall", "F1", "LogLoss", "AUC_ROC",
                 "Kappa"])
    idx = 0
    df = read_data_for_preparation(DataSource.HIST_DATA, Pair.EURUSD_1_2024, 3_000)

    supplier = [lin_reg_supplier, ridge_supplier, sgd_supplier, svr_supplier, rand_for_supplier]
    stops = [10, 20, 30, 50, 70, 100]
    limits = [10, 20, 30, 50, 100, 200]
    sizes = [0.2, 0.5, 1]
    metadata_supplier = [lin_reg_meta_data_supplier, ridge_meta_data_supplier, sgd_meta_data_supplier,
                         svr_meta_data_supplier,
                         rand_for_meta_data_supplier]

    iterations = len(supplier) * len(stops) * len(limits) * len(sizes)

    for model_sup, met_data in zip(
            supplier,
            metadata_supplier
    ):
        for stop in stops:
            for limit in limits:
                for size in sizes:
                    print(f"Iteration {idx} / {iterations}")
                    try:
                        name, train_length, pred_length = met_data()
                        err = execute_for_parameter(df, stop, limit, size, model_sup, train_length, pred_length)
                        err["model"] = name
                        err["stop"] = stop
                        err["limit"] = limit
                        err["size"] = size
                        err = pd.DataFrame(data=err, index=[idx])
                        errors = pd.concat([err, errors])
                        idx += 1
                    except Exception as e:
                        print("===========")
                        print(e)

                errors.to_csv("./backtest_results_ratios.csv", index=False)
    errors.to_csv("./backtest_results_ratios.csv", index=False)
