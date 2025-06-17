from abc import ABC

import numpy as np
import pandas as pd
from keras.api.metrics import MeanSquaredError, RootMeanSquaredError, MeanAbsoluteError, MeanAbsolutePercentageError, \
    MeanSquaredLogarithmicError, LogCoshError

from zpython.training.regression.regression_model_trainer import RegressionModelTrainer
from zpython.util.market_regime import MarketRegimeDetector
from zpython.util.model_data_creator import get_model_data_for_regime, ModelMarketRegime
from zpython.util.model_market_regime import ModelMarketRegimeDetector
from zpython.util.training.metric import ProfitHitRatioMetric, LossHitRatioMetric, NoneHitRatioMetric


class SequenceRegressionModelTrainer(RegressionModelTrainer, ABC):

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

    def _create_input_output_sequences(self, data: list[pd.DataFrame], original_data: list[pd.DataFrame],
                                       reduced_data: list[np.ndarray], target_column_idx):

        input_length = self._get_max_input_length()
        output_length = self._get_output_length()

        if output_length > input_length:
            raise Exception("Input-Length must be greater than Output-Length")

        input_data_np = [df[:input_length, :] for df in reduced_data]
        output_data_np = [df.to_numpy()[:, target_column_idx].reshape(-1, 1)[input_length:, :] for df in original_data]

        input_sequences = np.stack(input_data_np)
        output_sequences = np.stack(output_data_np)

        return input_sequences, output_sequences

    def _get_data_selector(self) -> str:
        return "SEQUENCE_REGRESSION"

    def _get_metrics(self) -> list:
        return [MeanSquaredError(), RootMeanSquaredError(), MeanAbsoluteError(), MeanAbsolutePercentageError(),
                MeanSquaredLogarithmicError(), LogCoshError(), ProfitHitRatioMetric(), LossHitRatioMetric(),
                NoneHitRatioMetric()]
