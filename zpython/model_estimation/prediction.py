import os

import pandas as pd
from keras.api.models import load_model

from zpython.util.model_market_regime import ModelMarketRegime
from zpython.util.path_util import from_relative_path
from zpython.util.training import custom_objects


def _model_name(name):
    return name.split("_")[0]


def _get_all_metrics(base_path: str, studies: list[str]):
    paths = [from_relative_path(f"{base_path}/{study}/a-metrics_{_model_name(study)}.csv") for study in studies]
    paths = [p for p in paths if os.path.exists(p)]
    metrics = [pd.read_csv(p) for p in paths]
    for metric, study in zip(metrics, studies):
        metric["study"] = study
    metrics = pd.concat(metrics)
    metrics = metrics.reset_index()
    return metrics


def _get_metrics_by_regime(base_path: str) -> dict[ModelMarketRegime, pd.DataFrame]:
    studies = os.listdir(from_relative_path(base_path))
    metrics = _get_all_metrics(base_path, studies)
    result = {}
    for regime in list(ModelMarketRegime):
        result[regime] = metrics[metrics["regime_id"] == regime.value]
    return result


def _load_best_models(base_path, metrics_by_regime):
    models = {}
    for regime in metrics_by_regime.keys():
        metrics = metrics_by_regime[regime]
        min_row = metrics.loc[metrics["val_loss"].idxmin()]
        trial = min_row["trial"]
        epoch = min_row["epoch"]
        study = min_row["study"]
        path = from_relative_path(
            f"{base_path}/{study}/trial_{trial}_epoch_{epoch}_{_model_name(study)}_{regime.name}.keras")
        models[regime] = load_model(path, custom_objects=custom_objects())

    return models


def load_best_models(base_path: str):
    metrics_by_regime = _get_metrics_by_regime(base_path)
    models = _load_best_models(base_path, metrics_by_regime)
    return models
