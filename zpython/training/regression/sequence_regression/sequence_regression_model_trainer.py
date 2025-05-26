from abc import ABC

import numpy as np

from zpython.training.regression.regression_model_trainer import RegressionModelTrainer


class SequenceRegressionModelTrainer(RegressionModelTrainer, ABC):

    def __init__(self, model_name: str, scaler_provider):
        super().__init__(model_name, scaler_provider)

    def _create_input_output_sequences(self, data: list[np.ndarray], reduced_data: list[np.ndarray], target_column_idx):

        input_length = self._get_max_input_length()
        output_length = self._get_output_length()

        if output_length > input_length:
            raise Exception("Input-Length must be greater than Output-Length")

        if len(data[0]) != input_length + output_length:
            raise Exception(f"Length of Data must be {input_length + output_length}, but was {len(data[0])}")

        input_data_np = [df[:input_length, :] for df in reduced_data]
        output_data_np = [df[:, target_column_idx].reshape(-1, 1)[input_length:, :] for df in data]

        input_sequences = np.stack(input_data_np)
        output_sequences = np.stack(output_data_np)

        return input_sequences, output_sequences

    def _get_data_selector(self) -> str:
        return "SEQUENCE_REGRESSION"
