import numpy as np
import pandas as pd

from zpython.prediction.regression.base_prediction import BasePrediction
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair


class CnnModelPrediction(BasePrediction):

    def __init__(self, start_time=pd.Timestamp(year=2024, month=1, day=1),
                 end_time=pd.Timestamp(year=2024, month=3, day=30),
                 bars_to_predict=None,
                 data_reader=None):
        super().__init__("cnn_log_ret",
                         DataSource.HIST_DATA,
                         Pair.EURUSD_5,
                         start_time,
                         end_time,
                         10000,
                         bars_to_predict,
                         data_reader)

    def prepare_data_scaled(self, data_source: DataSource, pair: Pair) -> tuple[list[pd.Timestamp], np.array]:
        df = self.data_reader(data_source.file_path(pair))
        df = self.slice_timeframe(df)
        df["logReturns"] = np.log(df["closeBid"] / df["closeBid"].shift(1)).dropna()
        df["logReturns"] = self.get_scaler().transform(df[["logReturns"]])
        parts = self.slice_partitions(df, pair.minutes(), 2)
        print("Extracting Input data...")
        inputs = np.stack([part["logReturns"].to_numpy() for part in parts])
        print("Extracting Timestamps...")
        timestamps = [part.index.max() for part in parts]

        return timestamps, inputs.reshape(inputs.shape[0], inputs.shape[1], 1)

    def output_length(self):
        return 2


if __name__ == "__main__":
    predictor = CnnModelPrediction()
    predictor.predict_and_save(14)
