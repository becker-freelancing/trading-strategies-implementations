import matplotlib
import numpy as np

from zpython.model.best_model_loader import _model_name
from zpython.util.model_data_creator import ModelMarketRegime

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from zpython.model.best_model_loader_classification import _get_metrics_by_regime

plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20
})

metrics_by_regime = _get_metrics_by_regime("models-bybit/CLASSIFICATION_240")

regime_groups = [
    [ModelMarketRegime.UP_LOW_VOLA_033, ModelMarketRegime.UP_LOW_VOLA_066, ModelMarketRegime.UP_LOW_VOLA_1],
    [ModelMarketRegime.UP_HIGH_VOLA_033, ModelMarketRegime.UP_HIGH_VOLA_066, ModelMarketRegime.UP_HIGH_VOLA_1],
    [ModelMarketRegime.SIDE_LOW_VOLA_033, ModelMarketRegime.SIDE_LOW_VOLA_066, ModelMarketRegime.SIDE_LOW_VOLA_1],
    [ModelMarketRegime.SIDE_HIGH_VOLA_033, ModelMarketRegime.SIDE_HIGH_VOLA_066, ModelMarketRegime.SIDE_HIGH_VOLA_1],
    [ModelMarketRegime.DOWN_LOW_VOLA_033, ModelMarketRegime.DOWN_LOW_VOLA_066, ModelMarketRegime.DOWN_LOW_VOLA_1],
    [ModelMarketRegime.DOWN_HIGH_VOLA_033, ModelMarketRegime.DOWN_HIGH_VOLA_066, ModelMarketRegime.DOWN_HIGH_VOLA_1]
]

colors = {
    "attentioncnn": "#FF0000",
    "cnngru": "#B22222",
    "deepcnn": "#DC143C",
    "multiscalecnn": "#DC143C",
    "simplecnn": "#CD5C5C",
    "bilstm": "#0000FF",
    "dropoutlstm": "#4169E1",
    "encodedecodelstm": "#00BFFF",
    "lstm": "#000080",
    "nndropout": "#008000",
    "nn": "#2E8B57",
    "nnresidual": "#32CD32",
    "transformer": "#FF8C00",
    "attentioncnn_single": "#FF0000",
    "cnngru_single": "#B22222",
    "deepcnn_single": "#DC143C",
    "multiscalecnn_single": "#DC143C",
    "simplecnn_single": "#CD5C5C",
    "bilstm_single": "#0000FF",
    "dropoutlstm_single": "#4169E1",
    "encodedecodelstm_single": "#00BFFF",
    "lstm_single": "#000080",
    "nndropout_single": "#008000",
    "nn_single": "#2E8B57",
    "nnresidual_single": "#32CD32",
    "transformer_single": "#FF8C00"
}

names = {
    "attentioncnn": "Attention CNN",
    "cnngru": "CNN + GRU",
    "deepcnn": "Deep CNN",
    "multiscalecnn": "Multi-Scale CNN",
    "simplecnn": "CNN",
    "bilstm": "Bi-LSTM",
    "dropoutlstm": "Dropout LSTM",
    "encodedecodelstm": "Encode-Decode LSTM",
    "lstm": "LSTM",
    "nndropout": "Dropout NN",
    "nn": "NN",
    "nnresidual": "Residual NN",
    "transformer": "Transformer",
    "attentioncnn_single": "Attention CNN",
    "cnngru_single": "CNN + GRU",
    "deepcnn_single": "Deep CNN",
    "multiscalecnn_single": "Multi-Scale CNN",
    "simplecnn_single": "CNN",
    "bilstm_single": "Bi-LSTM",
    "dropoutlstm_single": "Dropout LSTM",
    "encodedecodelstm_single": "Encode-Decode LSTM",
    "lstm_single": "LSTM",
    "nndropout_single": "Dropout NN",
    "nn_single": "NN",
    "nnresidual_single": "Residual NN",
    "transformer_single": "Transformer"
}


def _get_color(name):
    return colors[name]


def _get_name(name):
    return names[name]


for regime in list(ModelMarketRegime):
    fig, axs = plt.subplots(1, 1)
    row = 0
    metr = metrics_by_regime[regime]
    metr["name"] = metr["study"].apply(_model_name)
    metr["color"] = metr["name"].apply(_get_color)
    metr["name"] = metr["name"].apply(_get_name)
    studies = np.unique(metr["study"].values)
    for study in studies:
        metr_for_study = metr[(metr["study"] == study) & (metr["epoch"] != 0)]
        min_for_study = metr_for_study.loc[metr_for_study["val_accuracy"].idxmax()]
        min_trial = min_for_study["trial"]
        mins = metr_for_study[metr_for_study["trial"] == min_trial]
        mv = np.max(mins["val_accuracy"])
        mvt = np.max(mins["accuracy"])
        color = mins["color"].iloc[0]
        l1 = axs.plot(mins["epoch"].values, mins["val_accuracy"].values,
                      label=f"{mins['name'].iloc[0]}_trial_{min_trial}",
                      color=color)
        axs.plot(mins["epoch"].values, mins["accuracy"].values, linestyle="--", color=l1[0].get_color())
    axs.set_title(regime.name)
    axs.set_ylim((0, 1))
    axs.legend()
    plt.tight_layout()
    plt.legend()
    plt.show()
