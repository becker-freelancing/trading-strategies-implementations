import numpy as np
import pandas as pd
from zpython.backtest_prediction.classification.base_prediction import BasePrediction

from zpython.util.data_source import DataSource
from zpython.util.pair import Pair


class ClassificationLimit30Stop10(BasePrediction):

    def __init__(self, start_time=pd.Timestamp(year=2024, month=1, day=1),
                 end_time=pd.Timestamp(year=2024, month=3, day=30),
                 bars_to_predict=None,
                 data_reader=None):
        super().__init__("classification_limit_30_stop_10",
                         DataSource.HIST_DATA,
                         Pair.EURUSD_5,
                         start_time,
                         end_time,
                         1000,
                         bars_to_predict,
                         data_reader)

    def prepare_data_scaled(self, data_source: DataSource, pair: Pair) -> tuple[list[pd.Timestamp], np.array]:
        df = self.data_reader(data_source.file_path(pair))
        df = self.slice_timeframe(df)
        df["closeBid"] = self.get_scaler().transform(df[["closeBid"]])
        parts = self.slice_partitions(df, pair.minutes(), 100)
        print("Extracting Input data...")
        inputs = np.stack([part["closeBid"].to_numpy() for part in parts])
        print("Extracting Timestamps...")
        timestamps = [part.index.max() for part in parts]

        return timestamps, inputs.reshape(inputs.shape[0], inputs.shape[1], 1)

    def output_labels(self) -> list[str]:
        return ["SellOutput", "BuyOutput", "NoneOutput"]


if __name__ == "__main__":
    predictor = ClassificationLimit30Stop10()
    predictor.predict_and_save(14)
