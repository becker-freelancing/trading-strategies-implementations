import matplotlib

matplotlib.use('TkAgg')

from zpython.estimation.losses_reader import read_loss
import numpy as np


def plot(axes, row, col, xs, ys, ylabel, color, linestyle, model_name, sel="min"):
    if sel == "min":
        idx = np.argmin(ys)
        val = np.min(ys)
        axes[row, col].scatter(idx, val, color=color)  # , label=f"Minimum ({idx:.0f}, {val:.7f})")
    else:
        idx = np.argmax(ys)
        val = np.max(ys)
        axes[row, col].scatter(idx, val, color=color)  # , label=f"Maximum ({idx:.0f}, {val:.7f})")
    axes[row, col].plot(xs, ys, color=color, linestyle=linestyle, label=model_name)
    axes[row, col].set_xlabel("Epoch")
    axes[row, col].set_ylabel(ylabel)
    axes[row, col].set_yscale("log")
    axes[row, col].legend()


def build_plots(path, axs, linestyle="-", color="blue", model_name="<model-name>"):
    losses = read_loss(path)

    # MSE,RMSE,MAE,MAPE,MSLE,LogCosh,R2

    if "Loss" in losses.columns:
        plot(axs, 0, 0, losses.index, losses["Loss"], "Loss", color, linestyle, model_name)

    plot(axs, 0, 1, losses.index, losses["MSE"], "MSE", color, linestyle, model_name)
    plot(axs, 1, 0, losses.index, losses["RMSE"], "RMSE", color, linestyle, model_name)
    plot(axs, 1, 1, losses.index, losses["MAE"], "MAE", color, linestyle, model_name)
    plot(axs, 2, 0, losses.index, losses["MAPE"], "MAPE", color, linestyle, model_name)
    plot(axs, 2, 1, losses.index, losses["MSLE"], "MSLE", color, linestyle, model_name)
    plot(axs, 3, 0, losses.index, losses["LogCosh"], "LogCosh", color, linestyle, model_name)
    plot(axs, 3, 1, losses.index, losses["R2"], "R2", color, linestyle, model_name, sel="max")
