import matplotlib.pyplot as plt

from zpython.estimation.error_plot_builer import build_plots
from zpython.util.path_util import from_relative_path_from_models_dir

if __name__ == "__main__":
    model_name = "cnn"
    path = from_relative_path_from_models_dir(f"HIST_DATA/{model_name}/{model_name}_losses_out.csv")

    fig, axs = plt.subplots(4, 2, figsize=(10, 5))
    build_plots(path, axs)
    plt.show()
