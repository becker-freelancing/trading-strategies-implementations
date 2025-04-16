from abc import abstractmethod
from multiprocessing import Lock

import numpy as np
from keras.api.metrics import MeanSquaredError, RootMeanSquaredError, MeanAbsoluteError, MeanAbsolutePercentageError, \
    MeanSquaredLogarithmicError, LogCoshError, R2Score
from keras.src.callbacks import Callback
from optuna import Trial

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
        print("Slicing data in partitions...")

        input_length = self._get_input_length()
        output_length = self._get_output_length()

        if output_length > input_length:
            raise Exception("Input-Length must be grater than Output-Length")

        # Zeitstempel und Indexarrays
        timestamps = data.index.values
        start_idx = np.arange(len(data))
        end_times = timestamps + np.timedelta64(input_length, "m")
        end_idx = np.searchsorted(timestamps, end_times)

        # Nur gültige Sequenzen
        valid = (end_idx - start_idx) == input_length
        start_idx = start_idx[valid]

        # NumPy-Array der Daten
        input_data_np = data.loc[:, data.columns != self._get_target_column()].to_numpy()
        output_data_np = data.loc[:, self._get_target_column()].to_numpy().reshape(-1, 1)

        # Vektorisiert: Indexmatrix für alle Fenster
        input_window_offsets = np.arange(input_length)
        input_window_indices = start_idx[:, None] + input_window_offsets  # shape: (n_windows, total_length)
        output_window_indices = (input_window_indices + input_length)[:, 0:output_length]
        output_window_indices = output_window_indices[np.all(output_window_indices < len(output_data_np), axis=1)]

        # Jetzt einfach per fancy indexing das 3D-Array bauen
        input_data_window = input_data_np[input_window_indices]
        output_data_window = output_data_np[output_window_indices]
        input_data_window = input_data_window[:len(output_data_window)]

        input_data_nan_mask = ~np.isnan(input_data_window).any(axis=(1, 2))
        input_data_window = input_data_window[input_data_nan_mask]
        output_data_window = output_data_window[input_data_nan_mask]

        output_data_nan_mask = ~np.isnan(output_data_window).any(axis=(1, 2))
        input_data_window = input_data_window[output_data_nan_mask]
        output_data_window = output_data_window[output_data_nan_mask]

        return input_data_window, output_data_window

    def _get_metrics(self) -> list:
        return [MeanSquaredError(), RootMeanSquaredError(), MeanAbsoluteError(), MeanAbsolutePercentageError(),
                MeanSquaredLogarithmicError(), LogCoshError(), R2Score()]

    def _get_custom_callbacks(self, trial: Trial, lock: Lock) -> list[Callback]:
        return [SaveMetricCallback(trial, self._get_metric_file_path(), lock, self._get_metric_columns())]
