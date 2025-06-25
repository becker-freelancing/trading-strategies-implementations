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
        while(metric["val_loss"].min() < -30 or metric["loss"].max() < -30):
            val_to_small = metric[metric["val_loss"] < -30]
            metric = _transform_rows(metric, val_to_small, "val_loss")
            to_small = metric[metric["loss"] < -30]
            metric = _transform_rows(metric, to_small, "loss")
        metric.to_csv(path, index=False)


def _transform_rows(metric, val_to_small, col):
    for idx, row in val_to_small.sort_values(["trial", "epoch"], ascending=False).iterrows():
        sub = metric[(metric["trial"] == row["trial"]) & (metric["regime_id"] == row["regime_id"])]["epoch"]
        max_idx = sub.max()
        sub_2 = val_to_small[(val_to_small["trial"] == row["trial"]) & (val_to_small["regime_id"] == row["regime_id"])]
        all_to_small = set(sub_2["epoch"].values) == set(sub.values)
        if all_to_small:
            metric = metric.drop(labels=sub_2.index, axis=0)
            return metric.reset_index(drop=True)
        if row["epoch"] == 0:
            after = metric[(metric["trial"] == row["trial"]) & (metric["epoch"] == row["epoch"] + 1) & (metric["regime_id"] == row["regime_id"])].iloc[0]
            row[col] = 0.8 * after[col]
        elif row["epoch"] == max_idx:
            after = metric[(metric["trial"] == row["trial"]) & (metric["epoch"] == row["epoch"] - 1) & (metric["regime_id"] == row["regime_id"])].iloc[0]
            row[col] = 0.8 * after[col]
        else:
            after = metric[(metric["trial"] == row["trial"]) & (metric["epoch"] == row["epoch"] + 1) & (metric["regime_id"] == row["regime_id"])].iloc[0]
            before = metric[(metric["trial"] == row["trial"]) & (metric["epoch"] == row["epoch"] - 1) & (metric["regime_id"] == row["regime_id"])].iloc[0]
            row[col] = 0.5 * (before[col] + after[col])
        metric.iloc[idx] = row

    return metric


base = "models-bybit/SEQUENCE_REGRESSION"
studies = os.listdir(from_relative_path(base))
m = _get_all_metrics(base, studies)
_transform(m)
print()
