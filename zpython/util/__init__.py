from zpython.util.data_split import analysis_data, valid_time_frames, train_data, validation_data
from zpython.util.path_util import from_relative_path


def split_on_gaps(data, time_frame):
    time_diffs = data["closeTime"].diff().dt.total_seconds()
    start_idx = 0
    dfs = []
    for i in range(1, len(data)):
        if time_diffs.iloc[i] > 60 * time_frame:
            dfs.append(data.iloc[start_idx:i])
            start_idx = i
    dfs.append(data.iloc[start_idx:])
    return dfs
