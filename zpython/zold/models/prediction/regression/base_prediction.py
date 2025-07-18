from abc import abstractmethod

import joblib
import numpy as np
import pandas as pd
from keras.models import Model
from keras.models import load_model
from zpython.training.regression.data_preparation import read_data
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair

from zpython.util.path_util import from_relative_path_from_models_dir


class BasePrediction:

    def __init__(self, model_name: str,
                 data_source: DataSource,
                 pair: Pair,
                 from_time: pd.Timestamp,
                 to_time: pd.Timestamp,
                 prediction_batch_size: int,
                 bars_to_predict=None,
                 data_reader=None):
        self.model_name = model_name
        self.data_source = data_source
        self.pair = pair
        self.from_time = from_time
        self.to_time = to_time
        self.prediction_batch_size = prediction_batch_size
        self.scaler = None
        self.bars_to_predict = bars_to_predict
        if data_reader is None:
            self.data_reader = read_data
        else:
            self.data_reader = data_reader

    def model_dir(self) -> str:
        models_dir = from_relative_path_from_models_dir(
            f"{self.data_source.name()}/{self.pair.name()}/{self.model_name}/")
        return models_dir

    def file_name_in_models_dir(self, file_name):
        return f"{self.model_dir()}{file_name}"

    def get_scaler(self):
        if self.scaler is not None:
            return self.scaler
        self.scaler = joblib.load(self.file_name_in_models_dir(f"{self.model_name}_scaler.pkl"))
        return self.scaler

    def get_model(self, epoch: int) -> Model:
        model = load_model(self.file_name_in_models_dir(f"{self.model_name}_{epoch}.keras"))
        return model

    def slice_timeframe(self, df: pd.DataFrame):
        if self.bars_to_predict is not None:
            df = df[df.index >= self.from_time]
            return df.iloc[:self.bars_to_predict]
        return df[(df.index >= self.from_time) & (df.index <= self.to_time)]

    def slice_partitions(self, df: pd.DataFrame, minutes_timeframe: int, elements: int) -> list[pd.DataFrame]:
        print("Slicing data in partitions...")

        df = self.slice_timeframe(df)
        timestamps = df.index.values
        end_times = timestamps + np.timedelta64(minutes_timeframe * elements, "m")
        start_idx = np.arange(len(df))
        end_idx = np.searchsorted(timestamps, end_times)
        results = [df.iloc[i:j] for i, j in zip(start_idx, end_idx) if j - i == elements]
        return results

    @abstractmethod
    def prepare_data_scaled(self, data_source: DataSource, pair: Pair) -> tuple[list[pd.Timestamp], np.array]:
        """

        :param data_source:
        :param pair:
        :return: Eine Tuple, bei welchen das erste Element eine Liste mit allen Zeitpunkten ist (Länge: N), für welche vorhergesagt wird
        und als zweites Element ein numpy Array welches die jeweiligen Input-Daten enthält. Es hat den Shape (N, Input-Länge, Anz. Features)
        """
        pass

    @abstractmethod
    def output_length(self):
        pass

    def prepare_batches(self) -> list[tuple[list[pd.Timestamp], np.array]]:
        """

        :return: Eine Liste, welche pro Batch ein Tuple enthält, welches als ersten Eintrag eine Liste von
        Zeitstempeln [Länge: B] enthält, zu dem vorhergesagt werden soll, sowie die Input Daten mit dem Shape (B, Input-Länge, Anz. Feature)
        """

        dates, data = self.prepare_data_scaled(self.data_source, self.pair)

        batch_dates = [dates[i:i + self.prediction_batch_size] for i in
                       range(0, len(dates), self.prediction_batch_size)]
        batch_data = [data[i:i + self.prediction_batch_size, ...] for i in
                      range(0, len(data), self.prediction_batch_size)]

        batches = [(batch_dates[i], batch_data[i]) for i in range(len(batch_dates))]
        return batches

    def predict_and_save(self, epoch: int):
        predictions = self.predict(epoch)
        print(f"{len(predictions)} Timestamps predicted ({self.from_time} to {self.to_time})")
        predictions["prediction"] = predictions["prediction"].apply(lambda x: [float(i) for i in x])
        predictions.to_csv(self.file_name_in_models_dir(f"prediction_{self.model_name}_{epoch}.csv.zip"),
                           compression="zip", index=False)

    def predict(self, epoch: int) -> pd.DataFrame:
        predictions = pd.DataFrame(columns=["closeTime", "prediction"])
        batches = self.prepare_batches()
        model = self.get_model(epoch)

        for batch_data in batches:
            dates = batch_data[0]
            input_data = batch_data[1]

            batch_prediction = model.predict(input_data)
            batch_prediction = batch_prediction.reshape(batch_prediction.shape[0], self.output_length())
            batch_prediction = self.get_scaler().inverse_transform(batch_prediction)

            current_prediction = [list(pred) for pred in batch_prediction]
            batch_prediction_df = pd.DataFrame(data={"closeTime": dates,
                                                     "prediction": current_prediction})

            predictions = pd.concat([predictions, batch_prediction_df])

        return predictions
