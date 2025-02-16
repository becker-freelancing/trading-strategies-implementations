import matplotlib

matplotlib.use('TkAgg')

import numpy as np
import pandas as pd
import ast


def read_loss(path):
    losses = pd.read_csv(path)
    losses.set_index("Epoch", inplace=True)
    return losses

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


def build_regression_plots(path, axs, linestyle="-", color="blue", model_name="<model-name>"):
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


def build_classification_plots(path, axs, linestyle="-", color="blue", model_name="<model-name>"):
    losses = read_loss(path)

    if "Loss" in losses.columns:
        plot(axs, 0, 0, losses.index, losses["Loss"], "Loss", color, linestyle, model_name)

    f1_0 = losses["F1_Score"].apply(lambda x: ast.literal_eval(x)[0] if x else None)
    f1_1 = losses["F1_Score"].apply(lambda x: ast.literal_eval(x)[1] if x else None)
    f1_2 = losses["F1_Score"].apply(lambda x: ast.literal_eval(x)[2] if x else None)

    plot(axs, 0, 1, losses.index, losses["Categorial_Crossentropy"], "Categorial_Crossentropy", color, linestyle,
         model_name)
    plot(axs, 1, 0, losses.index, losses["Categorical_Accuracy"], "Categorical_Accuracy", color, linestyle, model_name,
         sel="max")
    plot(axs, 1, 1, losses.index, f1_0, "F1 (Klasse 0)", color, linestyle, model_name, sel="max")
    plot(axs, 2, 0, losses.index, f1_1, "F1 (Klasse 1)", color, linestyle, model_name, sel="max")
    plot(axs, 2, 1, losses.index, f1_2, "F1 (Klasse 2)", color, linestyle, model_name, sel="max")
