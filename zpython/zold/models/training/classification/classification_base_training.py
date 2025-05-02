from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from keras.api.callbacks import Callback
from keras.api.metrics import F1Score, CategoricalCrossentropy
from keras.src.metrics import CategoricalAccuracy
from zpython.training.base_training import BaseTraining
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair


class EpochEndCallback(Callback):

    def __init__(self, file_name_formatter, model_name):
        super().__init__()
        self.file_name = file_name_formatter(f'{model_name}_losses.csv')
        self.epoch = -1
        with open(self.file_name, 'w') as loss_out:
            loss_out.write(
                "Epoch,Loss,Categorial_Crossentropy,Categorical_Accuracy,F1_Score\n")

    def on_train_end(self, logs=None):
        self.epoch += 1
        with open(self.file_name, 'a') as loss_out:
            f1 = [float(f) for f in list(logs['f1_score'].numpy())]
            loss_out.write(
                f"{self.epoch},{logs['loss']},{logs['categorical_crossentropy']},{logs['categorical_accuracy']},{f1}\n")


class ClassificationBaseTraining(BaseTraining, ABC):

    def __init__(self, model_name: str, data_source: DataSource, pair: Pair, from_time: pd.Timestamp,
                 to_time: pd.Timestamp):
        super().__init__(model_name, data_source, pair, from_time, to_time)

    @abstractmethod
    def read_raw_expected(self):
        pass

    def slice_partitions(self, df: pd.DataFrame, minutes_timeframe: int, elements: int) -> (
            list[pd.Timestamp], list[pd.DataFrame]):
        print("Slicing data in partitions...")
        timestamps = df.index.values
        end_times = timestamps + np.timedelta64(minutes_timeframe * elements, "m")
        df_len = len(df)
        start_idx = np.arange(df_len)
        end_idx = np.searchsorted(timestamps, end_times)
        res = [(df.iloc[j].name, df.iloc[i:j]) for i, j in zip(start_idx, end_idx) if j - i == elements and j < df_len]
        dates = [t[0] for t in res]
        result = [t[1] for t in res]
        return dates, result

    def get_metrics(self) -> list:
        return [
            CategoricalCrossentropy(),
            CategoricalAccuracy(),
            F1Score()
        ]

    def epoch_end_Callback(self) -> Callback:
        return EpochEndCallback(self.file_name_in_models_dir, self.model_name)
