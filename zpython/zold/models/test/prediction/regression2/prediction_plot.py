import matplotlib
import numpy as np

matplotlib.use("TkAgg")

from zpython.models.test.prediction.regression2.data_preparation import read_data_and_generate_features_without_labels
from zpython.models.test.prediction.regression2.regressors import svr, svr_best_parameters
from zpython.models.test.prediction.regression2.regression_util import slice_data, regression
from zpython.util.pair import Pair
import matplotlib.pyplot as plt


def do_prediction(df, train_length, pred_length, regressor):
    x_train, y_train, x_pred, y_exp = slice_data(df, 2 * train_length + 10 + pred_length, train_length, pred_length)
    y_train_act, y_act = regression(x_train, y_train, x_pred, regressor())
    return y_train, y_train_act, y_exp, y_act


if __name__ == "__main__":
    time_frame = Pair.EURUSD_1_2024
    regressor = svr
    parameters = svr_best_parameters(time_frame)
    only_best_parameters = False

    pred_length = 180
    df = read_data_and_generate_features_without_labels(time_frame)

    best_y_train, best_y_train_act, best_y_exp, best_y_act = do_prediction(df, parameters, pred_length, regressor)

    plt.plot(list(range(len(best_y_exp))), best_y_exp, "--", label="Actual Y-Test")
    plt.plot(list(range(len(best_y_exp))), best_y_act, label=f"Best Y-Test Train-Length = {parameters}")

    if not only_best_parameters:
        for train_len in np.arange(start=5, stop=1000, step=20):
            y_train, y_train_act, y_exp, y_act = do_prediction(df, train_len, pred_length, regressor)
            plt.plot(list(range(len(y_act))), y_act, label=f"Train-Length = {train_len}")

    plt.legend()
    plt.show()
