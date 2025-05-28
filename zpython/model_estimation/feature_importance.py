import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import torch
import tqdm
from keras.api.models import load_model
from torch.utils.data import DataLoader

from zpython.training.data_set import FeatureShuffleTensorDataSet
from zpython.training.regression.nn.nn_regression_trainer import NNRegressionTrainer
from zpython.util.path_util import from_relative_path

######################################
STUDY_NAME = None
CALCULATION_DATA_SIZE = 3000


######################################

def get_names():
    if STUDY_NAME is not None:
        return [STUDY_NAME]
    return os.listdir(from_relative_path("models-bybit"))


names = get_names()

trainer = NNRegressionTrainer()
feature_names = [
    "volume",
    "logReturn_lowBid_1min",
    "logReturn_lowBid_2min",
    "logReturn_lowBid_3min",
    "logReturn_lowBid_6min",
    "logReturn_lowBid_9min",
    "logReturn_lowBid_12min",
    "logReturn_closeBid_2min",
    "logReturn_closeBid_3min",
    "logReturn_closeBid_6min",
    "logReturn_closeBid_9min",
    "logReturn_closeBid_12min",
    "logReturn_highBid_1min",
    "logReturn_highBid_2min",
    "logReturn_highBid_3min",
    "logReturn_highBid_6min",
    "logReturn_highBid_9min",
    "logReturn_highBid_12min",
    "ATR_14",
    "ATR_5",
    "ATR_7",
    "ATR_10",
    "ATR_18",
    "EMA_20",
    "EMA_10",
    "EMA_5",
    "EMA_30",
    "RSI_14",
    "RSI_7",
    "RSI_20",
    "MACD_12_26_9",
    "MACD_Signal_12_26_9",
    "BB_Upper_20",
    "BB_Middle_20",
    "BB_Lower_20",
    "BB_Upper_15",
    "BB_Middle_15",
    "BB_Lower_15",
    "BB_Upper_25",
    "BB_Middle_25",
    "BB_Lower_25",
    "momentum_2",
    "momentum_3",
    "momentum_6",
    "momentum_9",
    "momentum_12",
    "logReturn_1m_t-1",
    "logReturn_1m_t-2",
    "logReturn_1m_t-3",
    "logReturn_1m_t-4",
    "logReturn_1m_t-5",
    "logReturn_1m_t-6",
]


def model_name(name):
    return name.split("_")[0]


def best_trial(name):
    metrics = pd.read_csv(from_relative_path(f"models-bybit/{name}/a-metrics_{model_name(name)}.csv"))
    min = metrics.iloc[metrics["val_root_mean_squared_error"].argmin()]
    return int(min["trial"]), int(min["epoch"])


def input_length(trial, name):
    trials = pd.read_csv(from_relative_path(f"models-bybit/{name}/a-trials_{model_name(name)}.csv"), quotechar='(',
                         dtype=str)
    trials["trial"] = trials["trial"].apply(eval)
    best = trials[trials["trial"] == trial].iloc[0]
    return int(best["input_length"])


def cpu():
    return torch.device("cpu")


def gpu():
    return torch.device("gpu")


def get_dataset(length):
    train_loader, val_loader = trainer._get_train_validation_data(input_length=length,
                                                                  val_data_size=CALCULATION_DATA_SIZE)
    return val_loader


def create_base_line(dataset, model):
    y_true = []
    device_cpu = cpu()
    preds = model.predict(dataset)
    ds = dataset.dataset
    for i in tqdm.tqdm(range(len(ds)), "Creating y_true"):
        y_true.append(ds[i][1].to(device_cpu).numpy())
    y_true = np.array(y_true)
    y_pred = preds
    baseline_mse = np.mean((y_true - y_pred) ** 2)
    return baseline_mse, y_true


def shuffle_feature(x, idx):
    shuffled_col = x[:, :, idx].reshape(-1)
    shuffled_col = shuffled_col[torch.randperm(shuffled_col.size(0))]
    x = x.clone()
    x[:, :, idx] = shuffled_col.reshape(x.shape[0], x.shape[1])
    return x


def feature_importance_for_feature(model, dataset, feature_idx, y_true):
    loader = DataLoader(FeatureShuffleTensorDataSet(dataset.dataset, feature_idx), shuffle=False)
    preds = model.predict(loader)
    mse = np.mean((y_true - preds) ** 2)
    return mse


def feature_importance(model, length):
    print("Create baseline...")
    baseline_mse, y_true = create_base_line(get_dataset(length), model)
    mses = []
    for i in tqdm.tqdm(range(len(feature_names)), "Feature importance for feature"):
        mse = feature_importance_for_feature(model, get_dataset(length), i, y_true)
        mses.append(mse)

    importances = [mse - baseline_mse for mse in mses]

    raw_importances = np.array(importances)
    mean_importance = np.mean(importances)
    min_importance = np.min(importances)
    max_importance = np.max(importances)

    data = []
    for i, feature in enumerate(feature_names):
        imp = raw_importances[i]
        rel_to_mean = 100 * (imp - mean_importance) / (max_importance - min_importance + 1e-8)
        rel_to_min = 100 * (imp - min_importance) / (max_importance - min_importance + 1e-8)
        data.append({
            "feature": feature,
            "feature_idx": i,
            "importance": imp,
            "mse": mses[i],
            "baseline_mse": baseline_mse,
            "relative_to_mean_%": rel_to_mean,
            "relative_to_min_%": rel_to_min
        })

    df = pd.DataFrame(data)
    return df


def calc_and_save(name):
    print(f"Predicting: {name}")
    trial, epoch = best_trial(name)
    length = input_length(trial, name)

    model = load_model(from_relative_path(f"models-bybit/{name}/trial_{trial}_epoch_{epoch}_{model_name(name)}.keras"))

    df = feature_importance(model, length)
    print(f"============================================== \n {name} \n===========================================")
    df.to_csv(from_relative_path(f"models-bybit/{name}/a-feature_importance_{model_name(name)}.csv"), index=False)


with ThreadPoolExecutor(max_workers=5) as pool:
    for n in names:
        if os.path.exists(from_relative_path(f"models-bybit/{n}/a-feature_importance_{model_name(n)}.csv")):
            print(f"Skip model: {n}")
            continue
        pool.submit(calc_and_save, n)
