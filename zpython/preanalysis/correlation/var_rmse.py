import os
import warnings
from concurrent.futures.thread import ThreadPoolExecutor

import numpy as np
import pandas as pd
import tqdm
from statsmodels.tsa.api import VAR

from zpython.indicators import create_multiple_indicators
from zpython.util import from_relative_path, validation_data

df = create_multiple_indicators(validation_data)
df = df.replace([np.inf, -np.inf], np.nan).dropna()

TD_1 = pd.Timedelta(minutes=1)
TD_31 = pd.Timedelta(minutes=30)


def split(train_length, split_idx) -> tuple[pd.DataFrame, np.ndarray]:
    split_time = df.index[int(split_idx)]
    train = df.loc[split_time - pd.Timedelta(minutes=train_length):split_time]
    val = df.loc[split_time + TD_1:split_time + TD_31]["logReturn_closeBid_1min"].values
    return train, val


def calc_rmse(model_lag, train_length, split_idx) -> np.ndarray | None:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        train, val = split(train_length, split_idx)
        if len(val) != 30:
            return None
        train = train.drop(columns=["VolumeSpike_5",
                                    "VolumeSpike_10",
                                    "VolumeSpike_20",
                                    "VolumeSpike_30",
                                    "VolumeSpike_50",
                                    "RSI_20_Greater_70",
                                    "RSI_20_Less_30",
                                    "RSI_14_Greater_70",
                                    "RSI_14_Less_30",
                                    "RSI_7_Greater_70",
                                    "RSI_7_Less_30",
                                    ])
        try:
            train = train.loc[:, (train != train.iloc[0]).any()]
            model = VAR(train)
            var_result = model.fit(maxlags=model_lag)
            forecast = var_result.forecast(train.values, steps=30)
            forecast = forecast[:, 7]
            rmse = np.sqrt((forecast - val) ** 2)
            return rmse
        except Exception as e:
            return None


split_idxs = np.random.randint(2000, len(df), size=500)

results = pd.DataFrame(columns=["input_length", "model_lag", "avg_rmse", "num_tries"])
write_path = from_relative_path("models-bybit/var/var-results.csv")

if os.path.exists(write_path):
    results = pd.read_csv(write_path)

for input_length in tqdm.tqdm(range(5, 1500, 15), "Input-Length iteration"):
    for lag in range(5, 250, 10):
        if lag >= input_length:
            continue
        if len(results[(results["input_length"] == input_length) & (results["model_lag"] == lag)]) > 0:
            continue
        with ThreadPoolExecutor(max_workers=20) as pool:
            rmses_for_lag = pool.map(lambda idx: calc_rmse(lag, input_length, idx), split_idxs)
        rmses_for_lag = list(rmses_for_lag)
        rmses_for_lag = [rmse for rmse in rmses_for_lag if rmse is not None]
        avg_rmse = np.mean(np.array(rmses_for_lag))

        data = {
            "input_length": input_length,
            "model_lag": lag,
            "avg_rmse": avg_rmse,
            "num_tries": len(rmses_for_lag)
        }

        results = pd.concat([results, pd.DataFrame(data=data, index=[0])], ignore_index=True)
        results.to_csv(write_path, index=False)
