import numpy as np
import pandas as pd

from zpython.prediction.classification.base_prediction import BasePrediction
from zpython.util.data_source import DataSource
from zpython.util.pair import Pair
from zpython.util.path_util import from_relative_path


class ClassificationLimit30Stop10(BasePrediction):

    def __init__(self, start_time=pd.Timestamp(year=2024, month=1, day=1),
                 end_time=pd.Timestamp(year=2024, month=3, day=30),
                 bars_to_predict=None,
                 data_reader=None):
        super().__init__("classification_limit_30_stop_10_multi_dim",
                         DataSource.HIST_DATA,
                         Pair.EURUSD_5,
                         start_time,
                         end_time,
                         1000,
                         bars_to_predict,
                         data_reader)

    def prepare_data_scaled(self, data_source: DataSource, pair: Pair) -> tuple[list[pd.Timestamp], np.array]:
        df = self.read_raw_expected()
        df = self.slice_timeframe(df)
        df = self.normalize_data(df)
        parts = self.slice_partitions(df, pair.minutes(), 100)
        print("Extracting Input data...")
        inputs = np.stack([part[self.input_columns()].to_numpy()[:100] for part in parts])
        print("Extracting Timestamps...")
        timestamps = [part.index.max() for part in parts]

        return timestamps, inputs.reshape(inputs.shape[0], inputs.shape[1], 6)

    def read_raw_expected(self):
        path = from_relative_path(
            f"training-data/classification/{self.data_source.value}_{self.pair.name()}_limit_30_stop_10.csv.zip")
        df = pd.read_csv(path, compression="zip")
        df["closeTime"] = pd.to_datetime(df["closeTime"])
        df.set_index("closeTime", inplace=True)
        return df

    def normalize_data(self, input_df):
        scalers = self.get_scaler()
        for column in self.input_columns():
            minmax = scalers[column]
            input_df.loc[:, column] = minmax.transform(input_df[[column]])
            self.scaler[column] = minmax
        return input_df

    def input_columns(self):
        return ["closeBid", "ema_5", "ema_10", "ema_50", "atr_14", "rsi_14"]

    def output_labels(self) -> list[str]:
        return ["SellOutput", "BuyOutput", "NoneOutput"]


if __name__ == "__main__":
    predictor = ClassificationLimit30Stop10()
    predictor.predict_and_save(14)
