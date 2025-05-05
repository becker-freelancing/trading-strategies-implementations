import joblib
import matplotlib

matplotlib.use("TkAgg")
import os
import numpy as np
import pandas as pd
import torch
from keras.api.models import load_model

from zpython.util.path_util import from_relative_path
from zpython.util.data_split import validation_data
from zpython.indicators.indicator_creator import create_indicators
from random import randint
import matplotlib.pyplot as plt
from concurrent.futures.thread import ThreadPoolExecutor

######################################
STUDY_NAME = None
RANDOM_SELECT = False
INDEX = 500


######################################

def get_names():
    if STUDY_NAME is not None:
        return [STUDY_NAME]
    return os.listdir(from_relative_path("models-bybit"))


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


def get_model(trial, epoch, name):
    return load_model(from_relative_path(f"models-bybit/{name}/trial_{trial}_epoch_{epoch}_{model_name(name)}.keras"))


def get_input_data_plot(length, idx, data):
    return data.iloc[idx - length:idx]["logReturn_closeBid_1min"].values


def get_output_data(split_idx, data):
    return data.iloc[split_idx:split_idx + 30]["logReturn_closeBid_1min"].values


def get_input_data(length, idx, data, scaler):
    df = data.iloc[idx - length:idx]
    df = scaler.transform(df)
    col_idx = data.columns.get_loc("logReturn_closeBid_1min")
    return np.delete(df, col_idx, axis=1)


def retransform(prediction, scaler):
    target_col_idx = np.where(scaler.feature_names_in_ == "logReturn_closeBid_1min")[0][0]
    dummy = np.zeros((len(prediction), len(scaler.feature_names_in_)))
    dummy[:, target_col_idx] = target_col_idx.reshape(-1, 1)
    dummy = scaler.inverse_transform(dummy)
    return dummy[:, target_col_idx]


def predict_and_plot(name, model, input_length, data, split_idx, scaler, xs):
    try:
        print(f"\tPredict with model {name}...")
        input_data = get_input_data(input_length, split_idx, data, scaler)
        input_data = torch.tensor(input_data).unsqueeze(0)
        prediction = model.predict(input_data)[0]
        print(prediction)
        prediction = retransform(prediction, scaler)
        print(prediction)
        plt.plot(xs, prediction, label=name)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    names = get_names()
    trials = [best_trial(name) for name in names]
    input_lengths = [input_length(trial[0], name) for trial, name in zip(trials, names)]
    models = [get_model(trial[0], trial[1], name) for trial, name in zip(trials, names)]
    scaler = joblib.load(from_relative_path("data-bybit/a-scaler.scaler"))
    # Load Input and Expected Output
    max_input_length = np.max(input_lengths)
    data = create_indicators(data_read_function=validation_data, limit=10000)
    data = data.dropna()
    split_idx = INDEX
    if RANDOM_SELECT:
        split_idx = randint(max_input_length, len(data))

    input_data = get_input_data_plot(max_input_length, split_idx, data)
    expected_output = get_output_data(split_idx, data)
    output_xs = np.arange(len(input_data), len(input_data) + 30)

    plt.plot(np.arange(0, len(input_data)), input_data, label="Input Data")
    plt.plot(output_xs, expected_output, label="Expected Output")

    print("Predicting...")

    with ThreadPoolExecutor(max_workers=1) as pool:
        for name, model, input_length in zip(names, models, input_lengths):
            pool.submit(predict_and_plot, name=name, model=model, input_length=input_length, data=data,
                        split_idx=split_idx, scaler=scaler, xs=output_xs)

    plt.legend()
    plt.show()
