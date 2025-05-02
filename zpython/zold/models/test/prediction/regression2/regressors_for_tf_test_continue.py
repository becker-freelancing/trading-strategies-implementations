import functools
import random
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from zpython.models.test.prediction.regression2.data_preparation import read_data_and_generate_features_without_labels
from zpython.models.test.prediction.regression2.error_calculation import calc_error
from zpython.models.test.prediction.regression2.regression_util import regression, slice_data
from zpython.models.test.prediction.regression2.regressors import all, all_names
from zpython.util.pair import Pair


def slice_data_multiple(df, train_length, pred_length, split_idxs):
    slices = [slice_data(df, split_idx, train_length, pred_length) for split_idx in split_idxs]
    return [slice for slice in slices if
            len(slice[0]) == train_length and len(slice[1]) == train_length and len(slice[2]) == pred_length and len(
                slice[3]) == pred_length]


def test_regression(argument_tuple, regressor_supplier):
    x_train, y_train, x_pred, y_pred = argument_tuple
    regressor = regressor_supplier()
    train_pred, pred = regression(x_train, y_train, x_pred, regressor)

    error_tuple = calc_error(y_train, train_pred, y_pred, pred)
    return error_tuple


def extract_tuple_elements(iterable, index):
    return [element[index] for element in iterable]


def accumulate_errors(errors):
    rmse_trains = extract_tuple_elements(errors, 0)
    mae_trains = extract_tuple_elements(errors, 1)
    r2_trains = extract_tuple_elements(errors, 2)
    rmse_tests = extract_tuple_elements(errors, 3)
    mae_tests = extract_tuple_elements(errors, 4)
    r2_tests = extract_tuple_elements(errors, 5)
    return (np.average(rmse_trains),
            np.average(mae_trains),
            np.average(r2_trains),
            np.average(rmse_tests),
            np.average(mae_tests),
            np.average(r2_tests))


def execute_for_regressor(df, train_length, pred_length, split_idxs, tests_per_model, regressor):
    slices = slice_data_multiple(df, train_length, pred_length, split_idxs)
    fixed_test_regression = functools.partial(test_regression, regressor_supplier=regressor)
    with ThreadPoolExecutor(max_workers=tests_per_model) as executor:
        regression_errors = executor.map(fixed_test_regression, slices)
        regression_errors = list(regression_errors)
        return accumulate_errors(regression_errors)


def filter_regressors(train_length, pred_length, executed, time_frame, regressor_names, regressors):
    base_mask = (executed["InputLength"] == train_length) & (executed["TestLength"] == pred_length) & (
                executed["TimeFrame"] == time_frame.minutes())

    names = []
    regs = []
    for i in range(len(regressor_names)):
        mask = base_mask & (executed["Model"] == regressor_names[i])
        filtered = executed[mask]
        if len(filtered) == 0:
            names.append(regressor_names[i])
            regs.append(regressors[i])

    return names, regs


def execute_for_regressors(df, train_length, pred_length, split_idxs, tests_per_model, errors, executed, time_frame,
                           regressor_names, regressors):
    fixed_execute_for_regressor = functools.partial(execute_for_regressor, df=df,
                                                    train_length=train_length, pred_length=pred_length,
                                                    split_idxs=split_idxs, tests_per_model=tests_per_model)
    regressor_names, regressors = filter_regressors(train_length, pred_length, executed, time_frame, regressor_names,
                                                    regressors)
    if len(regressor_names) == 0:
        return errors
    with ThreadPoolExecutor(max_workers=len(regressor_names)) as executor:
        errors_per_regressor = executor.map(lambda regressor: fixed_execute_for_regressor(regressor=regressor),
                                            regressors)
        errors_per_regressor = list(errors_per_regressor)
        for regressor_name, errors_for_regressor in zip(regressor_names, errors_per_regressor):
            curr_error = pd.DataFrame(data={
                "Model": regressor_name,
                "InputLength": train_length,
                "TestLength": pred_length,
                "TimeFrame": time_frame.minutes(),
                "RMSE_TRAIN": errors_for_regressor[0],
                "MAE_TRAIN": errors_for_regressor[1],
                "R2_TRAIN": errors_for_regressor[2],
                "RMSE_TEST": errors_for_regressor[3],
                "MAE_TEST": errors_for_regressor[4],
                "R2_TEST": errors_for_regressor[5]
            }, index=[0])
            errors = pd.concat([errors, curr_error], ignore_index=True)

        return errors


if __name__ == "__main__":
    errors = pd.DataFrame(
        columns=["Model", "InputLength", "TestLength", "TimeFrame", "RMSE_TRAIN", "MAE_TRAIN", "R2_TRAIN", "RMSE_TEST",
                 "MAE_TEST", "R2_TEST"])

    executed = pd.read_csv("./regressors_for_tf_test.csv")
    errors = executed

    time_frames = [Pair.EURUSD_1_2024, Pair.EURUSD_5_2024, Pair.EURUSD_15_2024, Pair.EURUSD_30_2024,
                   Pair.EURUSD_60_2024, Pair.EURUSD_1440]
    train_lengths = np.arange(start=5, stop=1000, step=20)
    pred_length = 180

    regressors = all()
    regressor_names = all_names()

    tests_per_model = 200

    num_iterations = len(time_frames) * len(train_lengths)
    curr_iteration = 0

    for time_frame in time_frames:

        df = read_data_and_generate_features_without_labels(time_frame)
        split_idxs = [random.randint(np.max(train_lengths) + 10, len(df) - pred_length - 10) for _ in
                      range(tests_per_model)]

        for train_length in train_lengths:
            curr_iteration += 1
            print(f"{curr_iteration} / {num_iterations}")
            errors = execute_for_regressors(df, train_length, pred_length, split_idxs, tests_per_model, errors,
                                            executed, time_frame, regressor_names, regressors)

            errors.to_csv("./regressors_for_tf_test.csv", index=False)
