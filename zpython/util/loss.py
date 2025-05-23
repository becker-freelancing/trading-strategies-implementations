import torch

torch.set_printoptions(precision=3, sci_mode=False)
import numpy as np
from keras.api.losses import Loss
from keras.api import ops
from keras.src.losses.loss import squeeze_or_expand_to_same_rank

EPSILON = 0.1
INF = 9999999999

def huber_loss_np(y_true, y_pred, delta=0.03):
    error = y_true - y_pred
    is_small_error = np.abs(error) <= delta

    squared_loss = 0.5 * error ** 2
    linear_loss = delta * (np.abs(error) - 0.5 * delta)

    return np.where(is_small_error, squared_loss, linear_loss).mean()


def _sls_for_long_if_high_before_low(y_pred, y_pred_argmax):
    # Suche Minima vor Max-Index
    num_rows, num_cols = ops.shape(y_pred)

    col_indices = ops.arange(num_cols)
    col_indices = ops.reshape(col_indices, (1, -1))
    mask = ops.cast(col_indices < ops.expand_dims(y_pred_argmax, axis=1), y_pred.dtype)
    masked_data = y_pred * mask + (1.0 - mask) * ops.full_like(y_pred, INF)
    min_per_row = ops.min(masked_data, axis=1)

    return min_per_row


def _sls_for_long_if_high_after_low(y_pred_min):
    return ops.where(y_pred_min >= 0, -EPSILON, y_pred_min)


def _sls_for_long(y_pred, y_pred_min, y_pred_argmax, y_pred_argmin):
    return ops.where(y_pred_argmax < y_pred_argmin,
                     _sls_for_long_if_high_before_low(y_pred, y_pred_argmax),
                     _sls_for_long_if_high_after_low(y_pred_min)
                     )


def _sls_for_short_if_low_after_high(y_pred_max):
    return ops.where(y_pred_max <= 0, EPSILON, y_pred_max)


def _sls_for_short_if_low_before_high(y_pred, y_pred_argmin):
    # Suche Maxima vor Min-Index
    num_rows, num_cols = ops.shape(y_pred)

    col_indices = ops.arange(num_cols)
    col_indices = ops.reshape(col_indices, (1, -1))
    mask = ops.cast(col_indices < ops.expand_dims(y_pred_argmin, axis=1), y_pred.dtype)
    masked_data = y_pred * mask + (1.0 - mask) * ops.full_like(y_pred, -INF)
    max_per_row = ops.max(masked_data, axis=1)

    return max_per_row


def _sls_for_short(y_pred, y_pred_max, y_pred_argmax, y_pred_argmin):
    return ops.where(y_pred_argmin < y_pred_argmax,
                     _sls_for_short_if_low_before_high(y_pred, y_pred_argmin),
                     _sls_for_short_if_low_after_high(y_pred_max)
                     )


def _indices_greater_than_value(x, y):
    y_expanded = ops.expand_dims(y, axis=1)
    mask = ops.greater_equal(x, y_expanded)
    mask_int = ops.cast(mask, dtype="int32")
    first_greater_indices = ops.argmax(mask_int, axis=1)
    return ops.where(ops.all(mask == False, axis=1), ops.full_like(first_greater_indices, -1), first_greater_indices)


def _indices_less_than_value(x, y):
    y_expanded = ops.expand_dims(y, axis=1)
    mask = ops.less_equal(x, y_expanded)
    mask_int = ops.cast(mask, dtype="int32")
    first_less_indices = ops.argmax(mask_int, axis=1)
    return ops.where(ops.all(mask == False, axis=1), ops.full_like(first_less_indices, -1), first_less_indices)


def _tp_reached_first_for_long(y_true_cumsum, tps, sls):
    y_true_greater_tp_indices = _indices_greater_than_value(y_true_cumsum, tps)  # TODO: Umgang mit TP nicht getroffen
    y_true_less_sl_indices = _indices_less_than_value(y_true_cumsum, sls)

    return ops.where(y_true_greater_tp_indices < y_true_less_sl_indices, ops.full_like(tps, True),
                     ops.full_like(tps, False))


def _tp_reached_first_for_short(y_true_cumsum, tps, sls):
    y_true_less_tp_indices = _indices_less_than_value(y_true_cumsum, tps)  # TODO: Umgang mit TP nicht getroffen
    y_true_greater_sl_indices = _indices_greater_than_value(y_true_cumsum, sls)

    return ops.where(y_true_less_tp_indices < y_true_greater_sl_indices, ops.full_like(tps, True),
                     ops.full_like(tps, False))


def _sl_reached_first_for_long(y_true_cumsum, tps, sls):
    y_true_greater_tp_indices = _indices_greater_than_value(y_true_cumsum, tps)  # TODO: Umgang mit TP nicht getroffen
    y_true_less_sl_indices = _indices_less_than_value(y_true_cumsum, sls)

    return ops.where(y_true_greater_tp_indices > y_true_less_sl_indices, ops.full_like(tps, True),
                     ops.full_like(tps, False))


def _sl_reached_first_for_short(y_true_cumsum, tps, sls):
    y_true_less_tp_indices = _indices_less_than_value(y_true_cumsum, tps)  # TODO: Umgang mit TP nicht getroffen
    y_true_greater_sl_indices = _indices_greater_than_value(y_true_cumsum, sls)

    return ops.where(y_true_less_tp_indices > y_true_greater_sl_indices, ops.full_like(tps, True),
                     ops.full_like(tps, False))


def _profits_for_long(tp_reached_indices, sl_reached_indices, tps, sls):
    return ops.where(tp_reached_indices == -1,
                     sls,
                     # Take-Profit nicht erreicht -> Stop-Loss erreicht, egal ob es wirklich erreicht wurde oder nicht
                     ops.where(sl_reached_indices == -1,
                               tps,  # Stop Loss nicht erreicht, aber Take-Profit
                               ops.where(tp_reached_indices < sl_reached_indices,
                                         tps,  # Take-Profit vor Stop-Loss erreicht
                                         sls  # Stop-Loss vor Take-Profit erreicht
                                         )
                               )
                     )


def _profits_for_short(tp_reached_indices, sl_reached_indices, tps, sls):
    return -1 * _profits_for_long(tp_reached_indices, sl_reached_indices, tps, sls)


class PNLLoss(Loss):

    def __init__(self):
        super().__init__("pnl", "sum_over_batch_size", None)

    def call(self, y_true, y_pred):
        y_true = ops.convert_to_tensor(y_true)
        y_pred = ops.convert_to_tensor(y_pred)
        y_true, y_pred = squeeze_or_expand_to_same_rank(y_true, y_pred)

        y_pred_cumsum = ops.cumsum(y_pred, axis=1)
        y_pred_max = ops.max(y_pred_cumsum, axis=1)
        y_pred_min = ops.min(y_pred_cumsum, axis=1)

        # Falls |High| > |Low| Long Position (1), sonst Short (-1)
        direction_factor = ops.where((ops.abs(y_pred_max) > ops.abs(y_pred_min)), 1, -1)

        # Bestimmung von SL und TP
        y_pred_argmax = ops.argmax(y_pred_cumsum, axis=1)
        y_pred_argmin = ops.argmin(y_pred_cumsum, axis=1)

        # Für Long-Positionen ist globales Maximum TP. Für Short ist globales Minimum TP
        tps = ops.where(direction_factor == 1, y_pred_max, y_pred_min)

        sls = ops.where(direction_factor == 1,
                        _sls_for_long(y_pred, y_pred_min, y_pred_argmax, y_pred_argmin),
                        _sls_for_short(y_pred, y_pred_max, y_pred_argmax, y_pred_argmin))

        # Für jeden Trade P&L berechnen
        y_true_cumsum = ops.cumsum(y_true, axis=1)

        tp_reached_indices = ops.where(direction_factor == 1,
                                       _indices_greater_than_value(y_true_cumsum, tps),
                                       _indices_less_than_value(y_true_cumsum, tps))

        sl_reached_indices = ops.where(direction_factor == 1,
                                       _indices_less_than_value(y_true_cumsum, sls),
                                       _indices_greater_than_value(y_true_cumsum, sls))

        profits = ops.where(direction_factor == 1,
                            _profits_for_long(tp_reached_indices, sl_reached_indices, tps, sls),
                            _profits_for_short(tp_reached_indices, sl_reached_indices, tps, sls))

        return -1 * profits
