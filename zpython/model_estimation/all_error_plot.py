import matplotlib
import numpy as np

from zpython.util.model_data_creator import ModelMarketRegime

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from zpython.model_estimation.prediction import _get_metrics_by_regime

metrics_by_regime = _get_metrics_by_regime("models-bybit/SEQUENCE_REGRESSION")

fig, axs = plt.subplots(6, 3)

for regime, row, col in zip(list(ModelMarketRegime), list(range(3)) * 3, [0, 1] * 6):
    metr = metrics_by_regime[regime]
    studies = np.unique(metr["study"].values)
    for study in studies:
        metr_for_study = metr[metr["study"] == study]
        min_for_study = metr_for_study.loc[metr_for_study["val_loss"].idxmin()]
        min_trial = min_for_study["trial"]
        mins = metr_for_study[metr_for_study["trial"] == min_trial]
        axs[row, col].plot(mins["epoch"].values, mins["val_loss"].values, label=f"{study}_trial_{min_trial}")
    axs[row, col].set_title(regime.name)

plt.tight_layout()
plt.legend()
plt.show()
