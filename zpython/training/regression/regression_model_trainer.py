from abc import abstractmethod
from threading import Lock

import numpy as np
import pandas as pd
from keras.src.callbacks import Callback
from optuna import Trial

from zpython.training.callbacks import SaveMetricCallback
from zpython.training.model_trainer import ModelTrainer
from zpython.util.data_split import validation_data, train_data
from zpython.util.market_regime import MarketRegimeDetector
from zpython.util.model_data_creator import ModelMarketRegime
from zpython.util.model_market_regime import ModelMarketRegimeDetector


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
    def _load_model_data_for_regime(self, data_read_fn,
                                    regime: ModelMarketRegime,
                                    max_input_length: int,
                                    output_length: int,
                                    regime_detector: MarketRegimeDetector,
                                    model_regime_detector: ModelMarketRegimeDetector,
                                    train: bool) -> tuple[
        list[pd.DataFrame], pd.DataFrame, MarketRegimeDetector, ModelMarketRegimeDetector]:
        pass


    def _get_target_column_idx(self, complete_data):
        target = self._get_target_column()
        return complete_data.columns.get_loc(target)

    def _create_unsplited_data(self, regime: ModelMarketRegime, load_train_data=True) -> tuple[
        list[np.ndarray], list[np.ndarray], int]:
        if load_train_data:
            slices, complete_data, self.regime_detector, self.model_regime_detector = self._load_model_data_for_regime(
                train_data,
                                                                                           regime,
                                                                                           self._get_max_input_length(),
                                                                                           self._get_output_length(),
                                                                                           self._get_regime_detector(),
                self._get_model_regime_detector(),
                                                                                           True)
            slices = self._get_scaler().fit_transform(slices, regime)
            reduced_slices = self._get_regime_pca().fit_transform(slices, regime)

            return slices, reduced_slices, self._get_target_column_idx(complete_data)
        else:
            slices, complete_data, self.regime_detector, self.model_regime_detector = self._load_model_data_for_regime(
                validation_data,
                                                                                           regime,
                                                                                           self._get_max_input_length(),
                                                                                           self._get_output_length(),
                                                                                           self._get_regime_detector(),
                self._get_model_regime_detector(),
                                                                                           False)
            slices = self._get_scaler().transform(slices, regime)
            reduced_slices = self._get_regime_pca().transform(slices, regime)
            return slices, reduced_slices, self._get_target_column_idx(complete_data)

    def _get_train_data(self, regime: ModelMarketRegime) -> tuple[np.ndarray, np.ndarray]:
        train_data, reduced_train_data, target_column_idx = self._create_unsplited_data(regime, load_train_data=True)
        return self._parse_input_output(train_data, reduced_train_data, target_column_idx)

    def _get_validation_data(self, regime: ModelMarketRegime) -> tuple[np.ndarray, np.ndarray]:
        validation_data, reduced_train_data, target_column_idx = self._create_unsplited_data(regime,
                                                                                             load_train_data=False)
        return self._parse_input_output(validation_data, reduced_train_data, target_column_idx)

    def _parse_input_output(self, data: list[np.ndarray],
                            reduced_data: list[np.ndarray], target_column_idx) -> tuple[np.ndarray, np.ndarray]:
        input_data, output_data = self._create_input_output_sequences(data, reduced_data,
                                                                      target_column_idx)
        output_data = output_data.reshape(-1, output_data.shape[1])
        return input_data, output_data

    def _get_custom_callbacks(self, trial: Trial, lock: Lock, regime: ModelMarketRegime) -> list[Callback]:
        return [SaveMetricCallback(trial, self._get_metric_file_path(), lock, self._get_metric_columns(), regime)]
