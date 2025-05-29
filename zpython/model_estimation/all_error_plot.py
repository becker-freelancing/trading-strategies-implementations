import matplotlib
import numpy as np

from zpython.model_estimation.prediction import _model_name
from zpython.util.model_data_creator import ModelMarketRegime

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from zpython.model_estimation.prediction import _get_metrics_by_regime

metrics_by_regime = _get_metrics_by_regime("models-bybit/SEQUENCE_REGRESSION")

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
    "transformer": "#FF8C00"
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
    "transformer": "Transformer"
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
        min_for_study = metr_for_study.loc[metr_for_study["val_loss"].idxmin()]
        min_trial = min_for_study["trial"]
        mins = metr_for_study[metr_for_study["trial"] == min_trial]
        mv = np.min(mins["val_loss"])
        mvt = np.min(mins["loss"])
        if mv < -30:
            print(f"Min Val {mins['name'].iloc[0]} {regime} trial: {min_trial} is {mv}")
        if mvt < -30:
            print(f"Min Loss {mins['name'].iloc[0]} {regime} trial: {min_trial} is {mv}")
        color = mins["color"].iloc[0]
        l1 = axs.plot(mins["epoch"].values, mins["val_loss"].values, label=f"{mins['name'].iloc[0]}_trial_{min_trial}",
                      color=color)
        axs.plot(mins["epoch"].values, mins["loss"].values, linestyle="--", color=l1[0].get_color())
    axs.set_title(regime.name)
    axs.set_ylim((-15, 1))
    axs.legend()
    plt.tight_layout()
    plt.legend()
    plt.show()
