import numpy as np
import pandas as pd
from zpython.prediction.base_prediction import BasePrediction

from zpython.training.regression.data_preparation import read_data
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair


class TransformerModelPrediction(BasePrediction):

    def __init__(self, start_time=pd.Timestamp(year=2024, month=1, day=1),
                 end_time=pd.Timestamp(year=2024, month=1, day=30),
                 bars_to_predict=None):
        super().__init__("transformer_model",
                         DataSource.HIST_DATA,
                         Pair.EURUSD_1,
                         start_time,
                         end_time,
                         10000,
                         bars_to_predict=bars_to_predict)

    def prepare_data_scaled(self, data_source: DataSource, pair: Pair) -> tuple[list[pd.Timestamp], np.array]:
        df = read_data(data_source.file_path(pair))
        df = self.slice_timeframe(df)
        df["closeBid"] = self.get_scaler().transform(df[["closeBid"]])
        parts = self.slice_partitions(df, pair.minutes(), 100)
        print("Extracting Input data...")
        inputs = np.stack([part["closeBid"].to_numpy() for part in parts])
        print("Extracting Timestamps...")
        timestamps = [part.index.max() for part in parts]

        return timestamps, inputs.reshape(inputs.shape[0], inputs.shape[1], 1)

    def output_length(self):
        return 30


if __name__ == "__main__":
    predictor = TransformerModelPrediction()
    predictor.predict_and_save(12)
