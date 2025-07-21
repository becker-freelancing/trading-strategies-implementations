import pandas as pd

from zpython.util.path_util import from_relative_path


class DataCache:
    cache = {}


def read_data(time_frame, pair="ETHPERP"):
    path = from_relative_path(f"data-bybit/{pair}_{time_frame}.csv")

    if not time_frame in list(DataCache.cache.keys()):
        df = pd.read_csv(path)
        df["closeTime"] = pd.to_datetime(df["closeTime"], format="%Y-%m-%d %H:%M:%S")
        df = df.sort_values("closeTime")
        DataCache.cache[time_frame] = df

    return DataCache.cache[time_frame]


def train_data(time_frame=1, pair="ETHPERP"):
    data = read_data(time_frame, pair)
    data = data[data["closeTime"] < pd.to_datetime("2024-05-01")]
    data = data.drop_duplicates()
    return data  # .iloc[:6000]


def analysis_data(time_frame=1):
    data = read_data(time_frame)
    data = data[data["closeTime"] < pd.to_datetime("2024-05-01")]
    data = pd.concat([
        data[data["closeTime"].dt.day == 1],
        data[data["closeTime"].dt.day == 10],
        data[data["closeTime"].dt.day == 20],
        data[(data["closeTime"] >= pd.to_datetime("2024-04-01")) & (data["closeTime"] < pd.to_datetime("2024-05-01"))]
    ])
    data = data.drop_duplicates()
    return data


def validation_data(time_frame=1):
    data = read_data(time_frame)
    data = data[
        (data["closeTime"] >= pd.to_datetime("2024-05-01")) &
        (data["closeTime"] < pd.to_datetime("2024-10-01"))
        ]
    return data


def test_data(time_frame=1):
    data = read_data(time_frame)
    data = data[
        (data["closeTime"] >= pd.to_datetime("2024-10-01")) &
        (data["closeTime"] < pd.to_datetime("2025-01-01"))
        ]
    return data


def backtest_data(time_frame=1, pair="ETHPERP"):
    data = read_data(time_frame, pair)
    data = data[
        (data["closeTime"] >= pd.to_datetime("2025-01-01")) &
        (data["closeTime"] <= pd.to_datetime("2025-06-17"))
        ]
    return data


def valid_time_frames():
    return [1, 2, 3, 5, 15]
