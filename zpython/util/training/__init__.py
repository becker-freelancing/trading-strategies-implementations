from zpython.util.training.loss import PNLLoss
from zpython.util.training.metric import ProfitHitRatioMetric, LossHitRatioMetric, NoneHitRatioMetric, MSE, RMSE, MAE, \
    MAPE, MSLE, LogCosh


def custom_objects():
    return {
        "PNLLoss": PNLLoss,
        "ProfitHitRatioMetric": ProfitHitRatioMetric,
        "LossHitRatioMetric": LossHitRatioMetric,
        "NoneHitRatioMetric": NoneHitRatioMetric,
        "MSE": MSE,
        "RMSE": RMSE,
        "MAE": MAE,
        "MAPE": MAPE,
        "MSLE": MSLE,
        "LogCosh": LogCosh
    }
