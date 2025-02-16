import numpy as np
import pandas as pd
from keras.api.layers import LSTM, Dense, Input
from keras.api.models import Model
from keras.api.models import Sequential
from keras.api.optimizers import Adam
from sklearn.base import BaseEstimator
from sklearn.preprocessing import MinMaxScaler

from zpython.training.classification.classification_base_training import ClassificationBaseTraining
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair
from zpython.util.path_util import from_relative_path


def build_model() -> Model:
    model = Sequential()

    # LSTM-Schicht
    model.add(Input(shape=(100, 6)))
    model.add(LSTM(64, activation='relu'))

    # Ausgabe-Schicht (3 Klassen: Kaufen, Verkaufen, Nichts tun) Reihenfolge in Kommentar stimmt nicht
    model.add(Dense(3, activation='softmax'))

    # Modell kompilieren
    return model


class ClassificationLimit30Stop10Training(ClassificationBaseTraining):

    def __init__(self):
        super().__init__("classification_limit_30_stop_10_multi_dim",
                         DataSource.HIST_DATA,
                         Pair.EURUSD_5,
                         pd.Timestamp(year=2023, month=1, day=1),
                         pd.Timestamp(year=2023, month=12, day=31))
        self.scaler = {}

    def build_model(self) -> Model:
        model = build_model()
        model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=self.get_metrics())
        return model

    def prepare_data_scaled(self, data_source: DataSource, pair: Pair) -> tuple[np.ndarray, np.ndarray]:
        df = self.read_raw_expected()
        output_df = self.slice_timeframe(df)

        input_df = self.slice_timeframe(df)
        input_df = self.normalize_data(input_df)
        dates, parts = self.slice_partitions(input_df, pair.minutes(), 100)

        print("Extracting Input data...")
        inputs = np.stack([part[self.input_columns()].to_numpy()[:100] for part in parts])

        print("Extracting Output data...")
        outputs = self.extract_output(output_df, dates)
        return inputs.reshape(inputs.shape[0], inputs.shape[1], len(self.input_columns())), outputs

    def normalize_data(self, input_df):
        for column in self.input_columns():
            minmax = MinMaxScaler()
            input_df.loc[:, column] = minmax.fit_transform(input_df[[column]])
            self.scaler[column] = minmax
        return input_df

    def input_columns(self):
        return ["closeBid", "ema_5", "ema_10", "ema_50", "atr_14", "rsi_14"]

    def read_raw_expected(self):
        path = from_relative_path(
            f"training-data/classification/{self.data_source.value}_{self.pair.name()}_limit_30_stop_10.csv.zip")
        df = pd.read_csv(path, compression="zip")
        df["closeTime"] = pd.to_datetime(df["closeTime"])
        df.set_index("closeTime", inplace=True)
        return df

    def get_fitted_scaler(self) -> BaseEstimator:
        return self.scaler

    def extract_output(self, output_df, part):
        output_df = output_df.loc[part]
        output = output_df[["SellOutput", "BuyOutput", "NoneOutput"]].to_numpy()
        return output


if __name__ == "__main__":
    training = ClassificationLimit30Stop10Training()
    training.train_model(30)
