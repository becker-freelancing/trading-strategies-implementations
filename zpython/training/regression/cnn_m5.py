import numpy as np
import pandas as pd
from keras.api.layers import Conv1D, Dense, Flatten, MaxPooling1D
from keras.api.models import Model
from keras.api.models import Sequential
from keras.api.optimizers import Adam
from sklearn.base import BaseEstimator
from sklearn.preprocessing import MinMaxScaler

from zpython.training.regression.data_preparation import read_data
from zpython.training.regression.regression_base_training import RegressionBaseTraining
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair


def build_model(input_shape, output_steps) -> Model:
    model = Sequential([
        Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=input_shape),
        MaxPooling1D(pool_size=2),
        Conv1D(filters=32, kernel_size=3, activation='relu'),
        Flatten(),
        Dense(50, activation='relu'),
        Dense(output_steps)
    ])
    return model


class CnnModelTraining(RegressionBaseTraining):

    def __init__(self):
        super().__init__("cnn_m5",
                         DataSource.HIST_DATA,
                         Pair.EURUSD_5,
                         pd.Timestamp(year=2023, month=1, day=1),
                         pd.Timestamp(year=2023, month=12, day=31))
        self.scaler = MinMaxScaler()

    def build_model(self) -> Model:
        model = build_model((100, 1), 30)
        model.compile(optimizer=Adam(learning_rate=0.001), loss="mse", metrics=self.get_metrics())
        return model

    def prepare_data_scaled(self, data_source: DataSource, pair: Pair) -> tuple[np.ndarray, np.ndarray]:
        df = read_data(data_source.file_path(pair))
        df = self.slice_timeframe(df)
        df["closeBid"] = self.scaler.fit_transform(df[["closeBid"]])
        parts = self.slice_partitions(df, pair.minutes(), 130)
        print("Extracting Input data...")
        inputs = np.stack([part["closeBid"].to_numpy()[:100] for part in parts])
        print("Extracting Output data...")
        outputs = np.stack([part["closeBid"].to_numpy()[100:] for part in parts])
        return inputs.reshape(inputs.shape[0], inputs.shape[1], 1), outputs

    def get_fitted_scaler(self) -> BaseEstimator:
        return self.scaler


if __name__ == "__main__":
    training = CnnModelTraining()
    training.train_model(30)
