import matplotlib

matplotlib.use('TkAgg')

from zpython.estimation.losses_reader import read_loss
import numpy as np


def plot(axes, row, col, xs, ys, ylabel, color, linestyle, sel="min"):
    if sel == "min":
        idx = np.argmin(ys)
        val = np.min(ys)
        axes[row, col].scatter(idx, val, color=color, label=f"Minimum ({idx:.0f}, {val:.7f})")
    else:
        idx = np.argmax(ys)
        val = np.max(ys)
        axes[row, col].scatter(idx, val, color=color, label=f"Maximum ({idx:.0f}, {val:.7f})")
    axes[row, col].plot(xs, ys, color=color, linestyle=linestyle)
    axes[row, col].set_xlabel("Epoch")
    axes[row, col].set_ylabel(ylabel)
    axes[row, col].set_yscale("log")


def build_plots(path, axs, linestyle="-", color="blue"):
    losses = read_loss(path)

    # MSE,RMSE,MAE,MAPE,MSLE,LogCosh,R2

    if "Loss" in losses.columns:
        plot(axs, 0, 0, losses.index, losses["Loss"], "Loss", color, linestyle)

    plot(axs, 0, 1, losses.index, losses["MSE"], "MSE", color, linestyle)
    plot(axs, 1, 0, losses.index, losses["RMSE"], "RMSE", color, linestyle)
    plot(axs, 1, 1, losses.index, losses["MAE"], "MAE", color, linestyle)
    plot(axs, 2, 0, losses.index, losses["MAPE"], "MAPE", color, linestyle)
    plot(axs, 2, 1, losses.index, losses["MSLE"], "MSLE", color, linestyle)
    plot(axs, 3, 0, losses.index, losses["LogCosh"], "LogCosh", color, linestyle)
    plot(axs, 3, 1, losses.index, losses["R2"], "R2", color, linestyle, sel="max")
