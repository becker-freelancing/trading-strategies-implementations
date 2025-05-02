import matplotlib.pyplot as plt
from zpython.estimation.error_plot_builer import build_regression_plots

from zpython.util.path_util import from_relative_path_from_models_dir

if __name__ == "__main__":

    model_names = ["cnn_2_in_out", "cnn_half_year_m5", "cnn_m5", "cnn_two_year_m5"]
    colors = ["black", "blue", "green", "red", "cyan", "magenta", "yellow"]

    fig, axs = plt.subplots(4, 2, figsize=(10, 5))

    for model_name, color in zip(model_names, colors):
        path = from_relative_path_from_models_dir(f"HIST_DATA/EURUSD_5/{model_name}/{model_name}_losses_out.csv")
        path_in = from_relative_path_from_models_dir(f"HIST_DATA/EURUSD_5/{model_name}/{model_name}_losses.csv")

        build_regression_plots(path, axs, color=color, model_name=model_name)
        build_regression_plots(path_in, axs, linestyle="--", color=color, model_name=model_name)

    plt.show()
