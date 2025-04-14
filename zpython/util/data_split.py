import pandas as pd

from zpython.util.path_util import from_relative_path


class DataCache:
    cache = None

def read_data():
    path = from_relative_path("data-bybit\\ETHUSDT_1.csv")

    if DataCache.cache is None:
        df = pd.read_csv(path)
        df["closeTime"] = pd.to_datetime(df["closeTime"], format="%Y-%m-%d %H:%M:%S")
        df = df.sort_values("closeTime")
        DataCache.cache = df

    return DataCache.cache


def train_data():
    data = read_data()
    data = data[data["closeTime"] < pd.to_datetime("2023-08-01")]
    data = data[
        (data["closeTime"].dt.day != 1) &
        (data["closeTime"].dt.day != 10) &
        (data["closeTime"].dt.day != 20)
        ]
    data = data.drop_duplicates()
    return data


def analysis_data():
    data = read_data()
    data = data[data["closeTime"] < pd.to_datetime("2023-09-01")]
    data = pd.concat([
        data[data["closeTime"].dt.day == 1],
        data[data["closeTime"].dt.day == 10],
        data[data["closeTime"].dt.day == 20],
        data[(data["closeTime"] >= pd.to_datetime("2023-08-01")) & (data["closeTime"] < pd.to_datetime("2023-09-01"))]
    ])
    data = data.drop_duplicates()
    return data


def validation_data():
    data = read_data()
    data = data[
        (data["closeTime"] >= pd.to_datetime("2023-09-01")) &
        (data["closeTime"] < pd.to_datetime("2024-02-01"))
        ]
    return data


def test_data():
    data = read_data()
    data = data[
        (data["closeTime"] >= pd.to_datetime("2024-02-01")) &
        (data["closeTime"] < pd.to_datetime("2024-05-01"))
        ]
    return data


def backtest_data():
    data = read_data()
    data = data[
        (data["closeTime"] >= pd.to_datetime("2024-05-01")) &
        (data["closeTime"] < pd.to_datetime("2025-04-01"))
        ]
    return data
