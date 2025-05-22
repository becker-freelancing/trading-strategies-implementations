import numpy as np


def huber_loss_np(y_true, y_pred, delta=0.03):
    error = y_true - y_pred
    is_small_error = np.abs(error) <= delta

    squared_loss = 0.5 * error ** 2
    linear_loss = delta * (np.abs(error) - 0.5 * delta)

    return np.where(is_small_error, squared_loss, linear_loss).mean()
