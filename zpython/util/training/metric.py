import torch

torch.set_printoptions(precision=3, sci_mode=False)
from keras.api.metrics import Metric, MeanSquaredError, RootMeanSquaredError, MeanAbsoluteError, \
    MeanAbsolutePercentageError, MeanSquaredLogarithmicError, LogCoshError
from keras.api import ops
from zpython.util.training.loss_metric_util import _simulate_trades_sequence


class ProfitHitRatioMetric(Metric):
    def __init__(self, name="profit_hit_ratio", **kwargs):
        super().__init__(name=name, **kwargs)
        self.successes = self.add_weight(name="successes", initializer="zeros")
        self.total = self.add_weight(name="total", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        # Simuliere die Trades
        direction_factor, sl_reached_indices, sls, tp_reached_indices, tps = _simulate_trades_sequence(y_pred, y_true)

        zeros = ops.zeros_like(tps)
        ones = ops.ones_like(tps)

        # Logik: wann war TP vor SL?
        profit_hit_before_loss = ops.where(tp_reached_indices < 0,
                                           zeros,
                                           ops.where(sl_reached_indices < 0,
                                                     ones,
                                                     ops.where(tp_reached_indices < sl_reached_indices,
                                                               ones,
                                                               zeros)))

        # Optional: sample weighting
        if sample_weight is not None:
            sample_weight = ops.cast(sample_weight, self.dtype)
            profit_hit_before_loss = ops.multiply(profit_hit_before_loss, sample_weight)

        # Zustände aktualisieren
        self.successes.assign_add(ops.sum(profit_hit_before_loss))
        self.total.assign_add(ops.cast(ops.size(profit_hit_before_loss), self.dtype))

    def result(self):
        return self.successes / (self.total + 1e-8)  # Schutz vor Division durch Null

    def reset_states(self):
        self.successes.assign(0.0)
        self.total.assign(0.0)


class LossHitRatioMetric(Metric):
    def __init__(self, name="loss_hit_ratio", **kwargs):
        super().__init__(name=name, **kwargs)
        self.successes = self.add_weight(name="successes", initializer="zeros")
        self.total = self.add_weight(name="total", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        direction_factor, sl_reached_indices, sls, tp_reached_indices, tps = _simulate_trades_sequence(y_pred, y_true)

        zeros = ops.zeros_like(tps, dtype="float32")
        ones = ops.ones_like(tps, dtype="float32")

        loss_hit_before_loss = ops.where(
            tp_reached_indices < 0,
            ones,  # TP nicht erreicht → immer erfolgreich (1)
            ops.where(
                sl_reached_indices < 0,
                zeros,  # SL nicht erreicht → erfolglos (0)
                ops.where(
                    tp_reached_indices < sl_reached_indices,
                    zeros,  # TP vor SL → erfolglos (0)
                    ones  # SL vor TP → erfolgreich (1)
                )
            )
        )

        if sample_weight is not None:
            sample_weight = ops.cast(sample_weight, self.dtype)
            loss_hit_before_loss = loss_hit_before_loss * sample_weight

        self.successes.assign_add(loss_hit_before_loss.sum())
        self.total.assign_add(ops.cast(ops.size(loss_hit_before_loss), self.dtype))

    def result(self):
        return self.successes / (self.total + 1e-8)

    def reset_states(self):
        self.successes.assign(0.0)
        self.total.assign(0.0)


class NoneHitRatioMetric(Metric):
    def __init__(self, name="none_hit_ratio", **kwargs):
        super().__init__(name=name, **kwargs)
        self.successes = self.add_weight(name="successes", initializer="zeros")
        self.total = self.add_weight(name="total", initializer="zeros")

    def update_state(self, y_true, y_pred, sample_weight=None):
        direction_factor, sl_reached_indices, sls, tp_reached_indices, tps = _simulate_trades_sequence(y_pred, y_true)

        zeros = ops.zeros_like(tps, dtype="float32")
        ones = ops.ones_like(tps, dtype="float32")

        none_hit_before_loss = ops.where(
            tp_reached_indices < 0,
            ops.where(
                sl_reached_indices < 0,
                ones,
                zeros
            ),
            zeros
        )

        if sample_weight is not None:
            sample_weight = ops.cast(sample_weight, self.dtype)
            none_hit_before_loss = none_hit_before_loss * sample_weight

        self.successes.assign_add(none_hit_before_loss.sum())
        self.total.assign_add(ops.cast(ops.size(none_hit_before_loss), self.dtype))

    def result(self):
        return self.successes / (self.total + 1e-8)

    def reset_states(self):
        self.successes.assign(0.0)
        self.total.assign(0.0)


def _slice_relevant_parts(y_true, y_pred):
    min_dim = min(ops.shape(y_true)[1], ops.shape(y_pred)[1])
    return y_true[:, :min_dim], y_pred[:, :min_dim]


def _transform_y_true(y_true, y_pred):
    if ops.shape(y_true) == ops.shape(y_pred):
        return y_true, y_pred
    y_true_cumsum = ops.cumsum(y_true, axis=1)
    y_true_max = ops.max(y_true_cumsum, axis=1)
    y_true_min = ops.min(y_true_cumsum, axis=1)
    stack = ops.stack([y_true_max, y_true_min], axis=1)
    return stack, y_pred


class MSE(MeanSquaredError):

    def __init__(self, name="mean_squared_error", dtype=None):
        super().__init__(name, dtype)

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true, y_pred = _transform_y_true(y_true, y_pred)
        return super().update_state(y_true, y_pred, sample_weight)


class RMSE(RootMeanSquaredError):

    def __init__(self, name="root_mean_squared_error", dtype=None):
        super().__init__(name, dtype)

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true, y_pred = _transform_y_true(y_true, y_pred)
        return super().update_state(y_true, y_pred, sample_weight)


class MAE(MeanAbsoluteError):

    def __init__(self, name="mean_absolute_error", dtype=None):
        super().__init__(name, dtype)

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true, y_pred = _transform_y_true(y_true, y_pred)
        return super().update_state(y_true, y_pred, sample_weight)


class MAPE(MeanAbsolutePercentageError):

    def __init__(self, name="mean_absolute_percentage_error", dtype=None):
        super().__init__(name, dtype)

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true, y_pred = _transform_y_true(y_true, y_pred)
        return super().update_state(y_true, y_pred, sample_weight)


class MSLE(MeanSquaredLogarithmicError):

    def __init__(self, name="mean_squared_logarithmic_error", dtype=None):
        super().__init__(name, dtype)

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true, y_pred = _transform_y_true(y_true, y_pred)
        return super().update_state(y_true, y_pred, sample_weight)


class LogCosh(LogCoshError):

    def __init__(self, name="logcosh", dtype=None):
        super().__init__(name, dtype)

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_true, y_pred = _transform_y_true(y_true, y_pred)
        return super().update_state(y_true, y_pred, sample_weight)
