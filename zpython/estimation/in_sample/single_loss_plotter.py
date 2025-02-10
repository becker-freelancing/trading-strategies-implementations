import matplotlib

matplotlib.use('TkAgg')

from zpython.estimation.in_sample.losses_reader import read_loss
from zpython.util.path_util import from_relative_path_from_models_dir
import matplotlib.pyplot as plt

model_name = "transformer_model_unscaled"

path = from_relative_path_from_models_dir(f"DataSource.HIST_DATA/{model_name}/{model_name}_losses.csv")
losses = read_loss(path)

# Loss,MSE,RMSE,MAE,MAPE,MSLE,LogCosh,R2

fig, axs = plt.subplots(4, 2, figsize=(10, 5))


def plot(axes, row, col, xs, ys, ylabel):
    axes[row, col].plot(xs, ys)
    axes[row, col].set_title(f"{ylabel} per Epoch")
    axes[row, col].set_xlabel("Epoch")
    axes[row, col].set_ylabel(ylabel)
    axes[row, col].set_yscale("log")


plot(axs, 0, 0, losses.index, losses["Loss"], "Loss")
plot(axs, 0, 1, losses.index, losses["MSE"], "MSE")
plot(axs, 1, 0, losses.index, losses["RMSE"], "RMSE")
plot(axs, 1, 1, losses.index, losses["MAE"], "MAE")
plot(axs, 2, 0, losses.index, losses["MAPE"], "MAPE")
plot(axs, 2, 1, losses.index, losses["MSLE"], "MSLE")
plot(axs, 3, 0, losses.index, losses["LogCosh"], "LogCosh")
plot(axs, 3, 1, losses.index, losses["R2"], "R2")
plt.show()
