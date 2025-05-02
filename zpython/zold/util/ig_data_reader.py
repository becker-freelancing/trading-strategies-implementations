import pandas as pd

from zpython.util.path_util import from_relative_path


def read_data(file_name) -> pd.DataFrame:
    read_path = from_relative_path("data-ig/" + file_name)
    date_format = "%Y-%m-%dT%H:%M:%S"

    df = pd.read_csv(read_path, parse_dates=['closeTime'], date_format=date_format)
    df.set_index("closeTime", inplace=True)
    df = df.sort_index()
    return df
