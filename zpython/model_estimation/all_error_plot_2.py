import matplotlib
import numpy as np

from zpython.model.best_model_loader import _model_name
from zpython.util.model_data_creator import ModelMarketRegime

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from zpython.model.best_model_loader import _get_metrics_by_regime
from collections import OrderedDict
from matplotlib.ticker import MaxNLocator

metrics_by_regime = _get_metrics_by_regime("models-bybit/SINGLE_REGRESSION")

regime_groups = [
    [[ModelMarketRegime.UP_LOW_VOLA_033, ModelMarketRegime.UP_LOW_VOLA_066, ModelMarketRegime.UP_LOW_VOLA_1],
     [ModelMarketRegime.UP_HIGH_VOLA_033, ModelMarketRegime.UP_HIGH_VOLA_066, ModelMarketRegime.UP_HIGH_VOLA_1]],
    [[ModelMarketRegime.SIDE_LOW_VOLA_033, ModelMarketRegime.SIDE_LOW_VOLA_066, ModelMarketRegime.SIDE_LOW_VOLA_1],
     [ModelMarketRegime.SIDE_HIGH_VOLA_033, ModelMarketRegime.SIDE_HIGH_VOLA_066, ModelMarketRegime.SIDE_HIGH_VOLA_1]],
    [[ModelMarketRegime.DOWN_LOW_VOLA_033, ModelMarketRegime.DOWN_LOW_VOLA_066, ModelMarketRegime.DOWN_LOW_VOLA_1],
     [ModelMarketRegime.DOWN_HIGH_VOLA_033, ModelMarketRegime.DOWN_HIGH_VOLA_066, ModelMarketRegime.DOWN_HIGH_VOLA_1]]
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

ordered_names = [
    'CNN',
    'Attention CNN',
    'CNN + GRU',
    'Deep CNN',
    'Multi-Scale CNN',
    'LSTM',
    'Bi-LSTM',
    'Dropout LSTM',
    'Encode-Decode LSTM',
    'NN',
    'Dropout NN',
    'Residual NN',
    'Transformer']


def _get_color(name):
    return colors[name]


def _get_name(name):
    return names[name]


for sub_group in regime_groups:
    fig, axs = plt.subplots(2, 3)
    for row, group in zip(range(2), sub_group):
        for col, regime in zip(range(3), group):
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
                l1 = axs[row, col].plot(mins["epoch"].values, mins["val_loss"].values, label=f"{mins['name'].iloc[0]}",
                                        color=color)
                axs[row, col].plot(mins["epoch"].values, mins["loss"].values, linestyle="--", color=l1[0].get_color())
            axs[row, col].set_title(regime.name)
            axs[row, col].set_ylim((-15, 1))
            axs[row, col].grid()
            axs[row, col].xaxis.set_major_locator(MaxNLocator(integer=True))
    handles = []
    labels = []

    for ax in axs.flat:
        h, l = ax.get_legend_handles_labels()
        handles.extend(h)
        labels.extend(l)

    unique = dict(OrderedDict(zip(labels, handles)))
    sorted_handles_labels = [(unique[label], label) for label in ordered_names if label in unique]

    plt.tight_layout()
    fig.legend(*zip(*sorted_handles_labels), loc='center left', bbox_to_anchor=(0.0, 0.5))
    plt.subplots_adjust(left=0.15)
    plt.show()
