from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, SGDRegressor, Ridge
from sklearn.svm import SVR


def svr():
    return SVR()


def svr_best_parameters(time_frame):
    return 5


def rand_for():
    return RandomForestRegressor()


def rand_for_best_parameters(time_frame):
    return 5


def lin_reg():
    return LinearRegression()


def lin_reg_best_parameters(time_frame):
    return 5


def sgd():
    return SGDRegressor()


def sgd_best_parameters(time_frame):
    return 985


def ridge():
    return Ridge()


def ridge_best_parameters(time_frame):
    return 65


def all():
    return [svr, lin_reg, sgd, ridge, rand_for]


def all_names():
    return ["svr", "lin_reg", "sgd", "ridge", "rand_for"]


def all_best_parameters():
    return [svr_best_parameters,
            lin_reg_best_parameters,
            sgd_best_parameters,
            ridge_best_parameters,
            rand_for_best_parameters]
