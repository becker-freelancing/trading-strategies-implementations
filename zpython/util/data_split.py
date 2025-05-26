import pandas as pd

from zpython.util.path_util import from_relative_path


class DataCache:
    cache = {}


def read_data(time_frame):
    path = from_relative_path(f"data-bybit/ETHUSDT_{time_frame}.csv")

    if not time_frame in list(DataCache.cache.keys()):
        df = pd.read_csv(path)
        df["closeTime"] = pd.to_datetime(df["closeTime"], format="%Y-%m-%d %H:%M:%S")
        df = df.sort_values("closeTime")
        DataCache.cache[time_frame] = df

    return DataCache.cache[time_frame]


def train_data(time_frame=1):
    data = read_data(time_frame)
    data = data[data["closeTime"] < pd.to_datetime("2023-08-01")]
    data = data[
        (data["closeTime"].dt.day != 1) &
        (data["closeTime"].dt.day != 10) &
        (data["closeTime"].dt.day != 20)
        ]
    data = data.drop_duplicates()
    return data  # .iloc[:10000]


def analysis_data(time_frame=1):
    data = read_data(time_frame)
    data = data[data["closeTime"] < pd.to_datetime("2023-09-01")]
    data = pd.concat([
        data[data["closeTime"].dt.day == 1],
        data[data["closeTime"].dt.day == 10],
        data[data["closeTime"].dt.day == 20],
        data[(data["closeTime"] >= pd.to_datetime("2023-08-01")) & (data["closeTime"] < pd.to_datetime("2023-09-01"))]
    ])
    data = data.drop_duplicates()
    return data


def validation_data(time_frame=1):
    data = read_data(time_frame)
    data = data[
        (data["closeTime"] >= pd.to_datetime("2023-09-01")) &
        (data["closeTime"] < pd.to_datetime("2024-02-01"))
        ]
    return data


def test_data(time_frame=1):
    data = read_data(time_frame)
    data = data[
        (data["closeTime"] >= pd.to_datetime("2024-02-01")) &
        (data["closeTime"] < pd.to_datetime("2024-05-01"))
        ]
    return data


def backtest_data(time_frame=1):
    data = read_data(time_frame)
    data = data[
        (data["closeTime"] >= pd.to_datetime("2024-05-01")) &
        (data["closeTime"] < pd.to_datetime("2025-04-01"))
        ]
    return data


def valid_time_frames():
    return [1, 2, 3, 5, 15]
