import os
from abc import abstractmethod

import joblib
import numpy as np
import pandas as pd
from keras.api.callbacks import Callback
from keras.api.metrics import MeanSquaredError, RootMeanSquaredError, MeanAbsoluteError, MeanAbsolutePercentageError, \
    MeanSquaredLogarithmicError, LogCoshError, R2Score
from keras.api.models import Model
from keras.api.utils import Progbar
from sklearn.base import BaseEstimator

from zpython.util.data_source import DataSource
from zpython.util.pair import Pair
from zpython.util.path_util import from_relative_path_from_models_dir


class EpochEndCallback(Callback):

    def __init__(self, file_name_formatter, model_name):
        super().__init__()
        self.file_name = file_name_formatter(f'{model_name}_losses.csv')
        self.epoch = -1
        with open(self.file_name, 'w') as loss_out:
            loss_out.write("Epoch,Loss,MSE,RMSE,MAE,MAPE,MSLE,LogCosh,R2\n")

    def on_train_end(self, logs=None):
        self.epoch += 1
        with open(self.file_name, 'a') as loss_out:
            loss_out.write(
                f"{self.epoch},{logs['loss']},{logs['mean_squared_error']},{logs['root_mean_squared_error']},{logs['mean_absolute_error']},{logs['mean_absolute_percentage_error']},{logs['mean_squared_logarithmic_error']},{logs['logcosh']},{logs['r2_score']}\n")


class ProgbarWithoutMetrics(Callback):
    def on_epoch_begin(self, epoch, logs=None):
        self.progbar = Progbar(target=self.params['steps'])

    def on_batch_end(self, batch, logs=None):
        self.progbar.update(batch + 1)

    def on_epoch_end(self, epoch, logs=None):
        self.progbar.update(self.params['steps'], finalize=True)


class RegressionBaseTraining:

    def __init__(self, model_name: str, data_source: DataSource, pair: Pair, from_time: pd.Timestamp,
                 to_time: pd.Timestamp):
        self.model_name = model_name
        self.data_source = data_source
        self.pair = pair
        self.from_time = from_time
        self.to_time = to_time

    @abstractmethod
    def build_model(self) -> Model:
        pass

    @abstractmethod
    def prepare_data_scaled(self, data_source: DataSource, pair: Pair) -> tuple[np.ndarray, np.ndarray]:
        pass

    @abstractmethod
    def get_fitted_scaler(self) -> BaseEstimator:
        pass


    def slice_timeframe(self, df: pd.DataFrame):
        return df[(df.index >= self.from_time) & (df.index <= self.to_time)]

    def slice_partitions(self, df: pd.DataFrame, minutes_timeframe: int, elements: int) -> list[pd.DataFrame]:
        print("Slicing data in partitions...")
        timestamps = df.index.values
        end_times = timestamps + np.timedelta64(minutes_timeframe * elements, "m")
        start_idx = np.arange(len(df))
        end_idx = np.searchsorted(timestamps, end_times)
        results = [df.iloc[i:j] for i, j in zip(start_idx, end_idx) if j - i == elements]
        return results

    def model_dir(self) -> str:
        models_dir = from_relative_path_from_models_dir(f"{self.data_source}/{self.model_name}/")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        return models_dir

    def file_name_in_models_dir(self, file_name):
        return f"{self.model_dir()}{file_name}"

    def get_metrics(self) -> list:
        return [MeanSquaredError(), RootMeanSquaredError(), MeanAbsoluteError(), MeanAbsolutePercentageError(),
                MeanSquaredLogarithmicError(), LogCoshError(), R2Score()]

    def train_model(self, epochs):
        data_for_prediction, expected_prediction = self.prepare_data_scaled(self.data_source, self.pair)
        joblib.dump(self.get_fitted_scaler(), self.file_name_in_models_dir(f"{self.model_name}_scaler.pkl"))

        model = self.build_model()
        model.summary()

        call = EpochEndCallback(self.file_name_in_models_dir, self.model_name)
        progbar = ProgbarWithoutMetrics()
        for epoch in range(epochs):
            print(f"Training ({epoch + 1} / {epochs})...")
            model.fit(data_for_prediction, expected_prediction,
                      epochs=1, batch_size=128,
                      verbose=0,
                      callbacks=[call, progbar])
            model.save(self.file_name_in_models_dir(f"{self.model_name}_{epoch}.keras"))
