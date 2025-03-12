from sklearn.metrics import root_mean_squared_error, r2_score, mean_absolute_error


def calc_error(Y_train, Y_train_actual, Y_test, Y_test_actual):
    rmse_train = root_mean_squared_error(Y_train, Y_train_actual)
    mae_train = mean_absolute_error(Y_train, Y_train_actual)
    r2_train = r2_score(Y_train, Y_train_actual)
    rmse_test = root_mean_squared_error(Y_test, Y_test_actual)
    mae_test = mean_absolute_error(Y_test, Y_test_actual)
    r2_test = r2_score(Y_test, Y_test_actual)

    return rmse_train, mae_train, r2_train, rmse_test, mae_test, r2_test

    # return {
    #     "RMSE_TRAIN": rmse_train,
    #     "MAE_TRAIN": mae_train,
    #     "R2_TRAIN": r2_train,
    #     "RMSE_TEST": rmse_test,
    #     "MAE_TEST": mae_test,
    #     "R2_TEST": r2_test
    # }
