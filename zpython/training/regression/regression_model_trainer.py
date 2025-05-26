from abc import abstractmethod
from threading import Lock

import numpy as np
import pandas as pd
from keras.src.callbacks import Callback
from optuna import Trial
from tqdm import tqdm

from zpython.training.callbacks import SaveMetricCallback
from zpython.training.model_trainer import ModelTrainer
from zpython.util.data_split import validation_data, train_data
from zpython.util.market_regime import MarketRegime, MarketRegimeDetector


def transform(scaler, data: dict[MarketRegime, list[pd.DataFrame]]) -> dict[MarketRegime, list[np.ndarray]]:
    for key in tqdm(data.keys(), "Scaling Data"):
        value = data[key]
        value = [scaler.transform(df) for df in value]
        data[key] = value
    return data

class RegressionModelTrainer(ModelTrainer):

    def __init__(self, model_name: str, scaler_provider):
        super().__init__(model_name, scaler_provider)

    @abstractmethod
    def _get_output_length(self) -> int:
        pass

    @abstractmethod
    def _get_target_column(self) -> str:
        pass

    @abstractmethod
    def _create_input_output_sequences(self, data: list[np.ndarray], reduced_data: list[np.ndarray], target_column_idx):
        pass

    @abstractmethod
    def _load_model_data_by_regime(self, data_read_fn, max_input_length: int, output_length: int,
                                   regime_detector: MarketRegimeDetector, train):
        pass


    def _get_target_column_idx(self, complete_data):
        target = self._get_target_column()
        return complete_data.columns.get_loc(target)

    def _create_unsplited_data(self, load_train_data=True) -> tuple[
        dict[MarketRegime, list[np.ndarray]], dict[MarketRegime, list[np.ndarray]], int]:
        if load_train_data:
            slices, complete_data, self.regime_detector = self._load_model_data_by_regime(train_data,
                                                                                   self._get_max_input_length(),
                                                                                   self._get_output_length(),
                                                                                          self._get_regime_detector(),
                                                                                          True)
            self._get_scaler().fit(complete_data)
            slices = transform(self._get_scaler(), slices)
            self._get_regime_pca().fit(complete_data, self._get_scaler())
            reduced_slices = self._get_regime_pca().transform(slices)

            self._save_scaler()
            self._save_regime_detector()
            self._save_pca()

            return slices, reduced_slices, self._get_target_column_idx(complete_data)
        else:
            slices, complete_data, self.regime_detector = self._load_model_data_by_regime(validation_data,
                                                                                   self._get_max_input_length(),
                                                                                   self._get_output_length(),
                                                                                          self._get_regime_detector(),
                                                                                          False)
            slices = transform(self._get_scaler(), slices)
            reduced_slices = self._get_regime_pca().transform(slices)
            return slices, reduced_slices, self._get_target_column_idx(complete_data)

    def _get_train_data(self) -> dict[MarketRegime, tuple[np.ndarray, np.ndarray]]:
        train_data, reduced_train_data, target_column_idx = self._create_unsplited_data(load_train_data=True)
        return self._parse_input_output(train_data, reduced_train_data, target_column_idx)

    def _get_validation_data(self) -> dict[MarketRegime, tuple[np.ndarray, np.ndarray]]:
        validation_data, reduced_train_data, target_column_idx = self._create_unsplited_data(load_train_data=False)
        return self._parse_input_output(validation_data, reduced_train_data, target_column_idx)

    def _parse_input_output(self, data: dict[MarketRegime, list[np.ndarray]],
                            reduced_data: dict[MarketRegime, list[np.ndarray]], target_column_idx) -> dict[
        MarketRegime, tuple[np.ndarray, np.ndarray]]:
        result = {}
        for regime in tqdm(data.keys(), "Create input- and output-sequences"):
            regime_data = data[regime]
            reduced_regime_data = reduced_data[regime]
            input_data, output_data = self._create_input_output_sequences(regime_data, reduced_regime_data,
                                                                          target_column_idx)
            output_data = output_data.reshape(-1, output_data.shape[1])
            result[regime] = (input_data, output_data)

        return result


    def _get_custom_callbacks(self, trial: Trial, lock: Lock, regime: MarketRegime) -> list[Callback]:
        return [SaveMetricCallback(trial, self._get_metric_file_path(), lock, self._get_metric_columns(), regime)]
