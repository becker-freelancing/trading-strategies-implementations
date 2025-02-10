import matplotlib.pyplot as plt

from zpython.estimation.error_plot_builer import build_plots
from zpython.util.path_util import from_relative_path_from_models_dir

if __name__ == "__main__":

    model_names = ["cnn", "cnn_two_year", "cnn_half_year"]
    colors = ["black", "blue", "green", "red", "cyan", "magenta", "yellow"]

    fig, axs = plt.subplots(4, 2, figsize=(10, 5))

    for model_name, color in zip(model_names, colors):
        path = from_relative_path_from_models_dir(f"DataSource.HIST_DATA/{model_name}/{model_name}_losses_out.csv")
        path_in = from_relative_path_from_models_dir(f"DataSource.HIST_DATA/{model_name}/{model_name}_losses.csv")

        build_plots(path, axs, color=color)
        build_plots(path_in, axs, linestyle="--", color=color)

    plt.show()
