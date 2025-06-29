from abc import ABC
from threading import Lock

import numpy as np
import pandas as pd
from keras.src.callbacks import Callback
from optuna import Trial

from zpython.training.callbacks import SaveMetricCallback
from zpython.training.model_trainer import ModelTrainer
from zpython.util.classification_model_data_creator import get_model_data_for_regime, ModelMarketRegime
from zpython.util.data_split import train_data, validation_data
from zpython.util.market_regime import MarketRegimeDetector
from zpython.util.model_market_regime import ModelMarketRegimeDetector


class ClassificationWithoutPcaModelTrainer(ModelTrainer, ABC):

    def __init__(self, model_name: str, scaler_provider):
        super().__init__(model_name, scaler_provider)

    def _load_model_data_for_regime(self, data_read_fn,
                                    regime: ModelMarketRegime,
                                    max_input_length: int,
                                    output_length: int,
                                    regime_detector: MarketRegimeDetector,
                                    model_regime_detector: ModelMarketRegimeDetector,
                                    train: bool):
        return get_model_data_for_regime(data_read_fn,
                                         regime,
                                         max_input_length,
                                         output_length,
                                         regime_detector,
                                         model_regime_detector)

    def _get_data_selector(self) -> str:
        return "CLASSIFICATION_240_WITHOUT_PCA"

    def _get_metrics(self) -> list:
        return ["accuracy", "categorical_accuracy"]

    def _get_output_length(self) -> int:
        return 3

    def _load_model_data_for_regime(self, data_read_fn,
                                    regime: ModelMarketRegime,
                                    max_input_length: int,
                                    output_length: int,
                                    regime_detector: MarketRegimeDetector,
                                    model_regime_detector: ModelMarketRegimeDetector,
                                    train: bool) -> tuple[
        list[pd.DataFrame], list[np.ndarray], pd.DataFrame, MarketRegimeDetector, ModelMarketRegimeDetector]:
        return get_model_data_for_regime(data_read_fn, regime, max_input_length, regime_detector, model_regime_detector)

    def _create_unsplited_data(self, regime: ModelMarketRegime, load_train_data=True) -> tuple[
        list[pd.DataFrame], list[pd.DataFrame], list[np.ndarray], list[np.ndarray]]:
        if load_train_data:
            def read_train(time_frame):
                return train_data().iloc[-100000:]

            slices, labels, complete_data, self.regime_detector, self.model_regime_detector = self._load_model_data_for_regime(
                read_train,
                regime,
                self._get_max_input_length(),
                240,
                self._get_regime_detector(),
                self._get_model_regime_detector(),
                True)
            transformed_slices = self._get_scaler().fit_transform(slices, regime)
            reduced_slices = [df.to_numpy() for df in transformed_slices]

            return transformed_slices, slices, reduced_slices, labels
        else:
            slices, labels, complete_data, self.regime_detector, self.model_regime_detector = self._load_model_data_for_regime(
                validation_data,
                regime,
                self._get_max_input_length(),
                240,
                self._get_regime_detector(),
                self._get_model_regime_detector(),
                False)
            transformed_slices = self._get_scaler().transform(slices, regime)
            reduced_slices = [df.to_numpy() for df in transformed_slices]
            return transformed_slices, slices, reduced_slices, labels

    def _parse_input_output(self, reduced_data: list[np.ndarray], labels: list[np.ndarray]) -> tuple[
        np.ndarray, np.ndarray]:
        input_data = np.stack(reduced_data)
        output_data = np.stack(labels)
        output_data = output_data.reshape(-1, output_data.shape[1])
        return input_data, output_data

    def _get_train_data(self, regime: ModelMarketRegime) -> tuple[np.ndarray, np.ndarray]:  # x und Y Train
        train_data, original_data, reduced_train_data, labels = self._create_unsplited_data(regime,
                                                                                            load_train_data=True)
        return self._parse_input_output(reduced_train_data, labels)

    def _get_custom_callbacks(self, trial: Trial, lock: Lock, regime: ModelMarketRegime) -> list[Callback]:
        return [SaveMetricCallback(trial, self._get_metric_file_path(), lock, self._get_metric_columns(), regime)]
