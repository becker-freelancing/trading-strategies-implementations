from abc import ABC

import numpy as np

from zpython.training.regression.regression_model_trainer import RegressionModelTrainer
from zpython.util.market_regime import MarketRegimeDetector
from zpython.util.model_data_creator import get_model_data_for_regime, ModelMarketRegime
from zpython.util.model_market_regime import ModelMarketRegimeDetector
from zpython.util.training.metric import ProfitHitRatioMetric, LossHitRatioMetric, NoneHitRatioMetric, MSE, RMSE, MAE, \
    MAPE, MSLE, LogCosh


class SingleRegressionModelTrainer(RegressionModelTrainer, ABC):

    def __init__(self, model_name: str, scaler_provider):
        super().__init__(model_name, scaler_provider)

    def _load_model_data_for_regime(self, data_read_fn,
                                    regime: ModelMarketRegime,
                                    max_input_length: int,
                                    output_length: int,
                                    regime_detector: MarketRegimeDetector,
                                    model_regime_detector: ModelMarketRegimeDetector,
                                    train: bool):
        if train:
            return get_model_data_for_regime(data_read_fn, regime, max_input_length, 30, regime_detector,
                                             model_regime_detector)
        else:
            return get_model_data_for_regime(data_read_fn, regime, max_input_length, 30, regime_detector,
                                             model_regime_detector)

    def _create_input_output_sequences(self, data: list[np.ndarray], reduced_data: list[np.ndarray], target_column_idx):

        input_length = self._get_max_input_length()
        output_length = self._get_output_length()

        if output_length > input_length:
            raise Exception("Input-Length must be greater than Output-Length")

        input_data_np = [df[:input_length, :] for df in reduced_data]
        output_data_np = [df[:, target_column_idx].reshape(-1, 1)[input_length:, :] for df in data]

        input_sequences = np.stack(input_data_np)
        output_sequences = np.stack(output_data_np)

        return input_sequences, output_sequences

    def _get_data_selector(self) -> str:
        return "SINGLE_REGRESSION"

    def _get_metrics(self) -> list:
        return [MSE(), RMSE(), MAE(), MAPE(), MSLE(), LogCosh(), ProfitHitRatioMetric(), LossHitRatioMetric(),
                NoneHitRatioMetric()]

    def _get_output_length(self):
        return 2

    def _get_target_column(self):
        return "logReturn_closeBid_1min"

    def _get_max_input_length(self) -> int:
        return 150
