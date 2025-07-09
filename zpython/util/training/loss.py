import torch

torch.set_printoptions(precision=3, sci_mode=False)
from keras.losses import Loss
from keras import ops
from zpython.util.training.loss_metric_util import _simulate_trades_sequence, _profits_for_short, _profits_for_long


class PNLLoss(Loss):

    def __init__(self, name="pnl", reduction="sum_over_batch_size", dtype=None):
        super().__init__(name, reduction, dtype)

    def call(self, y_true, y_pred):
        direction_factor, sl_reached_indices, sls, tp_reached_indices, tps = _simulate_trades_sequence(y_pred, y_true)
        profits = ops.where(direction_factor == 1,
                            _profits_for_long(tp_reached_indices, sl_reached_indices, tps, sls),
                            _profits_for_short(tp_reached_indices, sl_reached_indices, tps, sls))

        return -1 * profits
