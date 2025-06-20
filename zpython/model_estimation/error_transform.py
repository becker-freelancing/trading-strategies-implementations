import os

import pandas as pd

from zpython.util.path_util import from_relative_path


def _model_name(name):
    return name.split("_")[0]


def _get_all_metrics(base_path: str, studies: list[str]):
    paths = [from_relative_path(f"{base_path}/{study}/a-metrics_{_model_name(study)}.csv") for study in studies]
    paths = [p for p in paths if os.path.exists(p)]
    metrics = [(p, pd.read_csv(p)) for p in paths]
    return metrics


def _transform(metrics):
    for path, metric in metrics:
        to_small = metric[(metric["loss"] < -30) | (metric["val_loss"] < -30)]
        n_valid = set(map(tuple, to_small[["trial", "regime_id"]].values))
        valid = metric[~metric[["trial", "regime_id"]].apply(tuple, axis=1).isin(n_valid)]
        valid.to_csv(path, index=False)


base = "models-bybit/SEQUENCE_REGRESSION"
studies = os.listdir(from_relative_path(base))
m = _get_all_metrics(base, studies)
_transform(m)
print()
