from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import numpy as np
from keras.api.metrics import MeanSquaredError, RootMeanSquaredError, MeanAbsoluteError, MeanAbsolutePercentageError, \
    MeanSquaredLogarithmicError, LogCoshError, R2Score
from keras.src.callbacks import Callback
from optuna import Trial
from tqdm import tqdm

from zpython.training.model_trainer import ModelTrainer


class SaveMetricCallback(Callback):

    def __init__(self, trial: Trial, file_name: str, lock: Lock, metric_columns):
        super().__init__()
        self.trial_id = trial.number
        self.file_name = file_name
        self.lock = lock
        self.metrics = metric_columns


    def on_epoch_end(self, epoch, logs=None):
        metrics = ",".join([str(logs[metric_name]) for metric_name in self.metrics])
        with self.lock:
            with open(self.file_name, "a") as file:
                file.write(
                    f"{self.trial_id},{epoch},{metrics}\n"
                )


class RegressionModelTrainer(ModelTrainer):

    def __init__(self, model_name: str, scaler_provider):
        super().__init__(model_name, scaler_provider)

    @abstractmethod
    def _get_output_length(self) -> int:
        pass

    @abstractmethod
    def _get_target_column(self) -> str:
        pass

    def _get_train_data(self) -> tuple[np.ndarray, np.ndarray]:
        train_data = self._create_unsplited_data(train_data=True)
        return self._parse_input_output(train_data)

    def _get_validation_data(self) -> tuple[np.ndarray, np.ndarray]:
        validation_data = self._create_unsplited_data(train_data=False)
        return self._parse_input_output(validation_data)

    def _parse_input_output(self, train_data):
        input_data, output_data = self._create_input_output_sequences(train_data)
        output_data = output_data.reshape(-1, output_data.shape[1])
        return input_data, output_data

    def _create_input_output_sequences(self, data):
        print("Creating input- and output-sequences...")

        input_length = self._get_max_input_length()
        output_length = self._get_output_length()

        if output_length > input_length:
            raise Exception("Input-Length must be greater than Output-Length")

        input_data_np = data.loc[:, data.columns != self._get_target_column()].to_numpy(dtype=np.float32)
        output_data_np = data.loc[:, self._get_target_column()].to_numpy(dtype=np.float32).reshape(-1, 1)

        total_length = len(data)
        max_start = total_length - input_length - output_length + 1

        input_sequences = []
        output_sequences = []

        def process_window(start_idx):
            input_end = start_idx + input_length
            output_end = input_end + output_length

            input_window = input_data_np[start_idx:input_end]
            output_window = output_data_np[input_end:output_end]

            if not np.isnan(input_window).any() and not np.isnan(output_window).any():
                return input_window, output_window
            return None

        with ThreadPoolExecutor() as executor:
            futures = list(executor.map(process_window, tqdm(range(max_start), desc="Slicing sequences")))

        # Filtere nur gültige Ergebnisse
        for result in tqdm(futures, desc="Filtering valid sequences"):
            if result is not None:
                x, y = result
                input_sequences.append(x)
                output_sequences.append(y)

        input_sequences = np.stack(input_sequences)
        output_sequences = np.stack(output_sequences)

        return input_sequences, output_sequences

    def _get_metrics(self) -> list:
        return [MeanSquaredError(), RootMeanSquaredError(), MeanAbsoluteError(), MeanAbsolutePercentageError(),
                MeanSquaredLogarithmicError(), LogCoshError(), R2Score()]

    def _get_custom_callbacks(self, trial: Trial, lock: Lock) -> list[Callback]:
        return [SaveMetricCallback(trial, self._get_metric_file_path(), lock, self._get_metric_columns())]
