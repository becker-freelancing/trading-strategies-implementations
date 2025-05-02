import matplotlib.pyplot as plt
from zpython.estimation.error_plot_builer import build_classification_plots

from zpython.util.path_util import from_relative_path_from_models_dir

if __name__ == "__main__":

    model_names = ["classification_limit_30_stop_10_multi_dim"]
    colors = ["black", "blue", "green", "red", "cyan", "magenta", "yellow"]

    fig, axs = plt.subplots(3, 2, figsize=(10, 5))

    for model_name, color in zip(model_names, colors):
        path = from_relative_path_from_models_dir(f"HIST_DATA/EURUSD_5/{model_name}/{model_name}_losses_out.csv")
        path_in = from_relative_path_from_models_dir(f"HIST_DATA/EURUSD_5/{model_name}/{model_name}_losses.csv")

        build_classification_plots(path, axs, color=color, model_name=model_name)
        build_classification_plots(path_in, axs, linestyle="--", color=color, model_name=model_name)

    plt.show()
