import numpy as np
import pandas as pd
from keras.api import layers
from keras.api.layers import Input
from keras.api.models import Model
from keras.api.optimizers import Adam
from sklearn.base import BaseEstimator
from sklearn.preprocessing import MinMaxScaler

from zpython.models.base_training import BaseTraining
from zpython.models.data_preparation import read_data
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair


def transformer_encoder(inputs, head_size=64, num_heads=4, ff_dim=128, dropout=0.1):
    """Ein einzelner Transformer-Block"""
    x = layers.MultiHeadAttention(num_heads=num_heads, key_dim=head_size)(inputs, inputs)
    x = layers.Dropout(dropout)(x)
    x = layers.LayerNormalization(epsilon=1e-6)(x)
    res = x + inputs  # Residual Connection

    # Feedforward-Netzwerk
    x = layers.Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(res)
    x = layers.Dropout(dropout)(x)
    x = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
    x = layers.LayerNormalization(epsilon=1e-6)(x)
    return x + res  # Residual Connection


def build_model(input_shape, output_steps, features=1):
    inputs = Input(shape=input_shape)
    # Transformer Encoder Stack (mehrere Blöcke)
    x = transformer_encoder(inputs)
    x = transformer_encoder(x)
    # Global Average Pooling für feste Dimension
    x = layers.GlobalAveragePooling1D()(x)
    # Dense-Schicht zur Vorhersage von 30 Werten
    outputs = layers.Dense(output_steps * features, activation="linear")(x)
    outputs = layers.Reshape((output_steps, features))(outputs)
    model = Model(inputs, outputs)
    return model


class TransformerModelTraining(BaseTraining):

    def __init__(self):
        super().__init__("transformer_model",
                         DataSource.HIST_DATA,
                         Pair.EURUSD_1,
                         pd.Timestamp(year=2023, month=1, day=1),
                         pd.Timestamp(year=2023, month=12, day=31))
        self.scaler = MinMaxScaler()

    def build_model(self) -> Model:
        model = build_model((100, 1), 30)
        model.compile(optimizer=Adam(learning_rate=0.001), loss="mse", metrics=self.get_metrics())
        return model

    def prepare_data_scaled(self, data_source: DataSource, pair: Pair) -> tuple[np.ndarray, np.ndarray]:
        df = read_data(data_source.file_path(pair))
        parts = self.slice_partitions(df, pair.minutes(), 130)
        print("Extracting Input data...")
        inputs = np.stack([part["closeBid"].to_numpy()[:100] for part in parts])
        print("Extracting Output data...")
        outputs = np.stack([part["closeBid"].to_numpy()[100:] for part in parts])
        return inputs.reshape(inputs.shape[0], inputs.shape[1], 1), outputs

    def get_fitted_scaler(self) -> BaseEstimator:
        pass


if __name__ == "__main__":
    training = TransformerModelTraining()
    training.train_model(30)
