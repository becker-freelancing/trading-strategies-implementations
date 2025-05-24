from threading import Lock

from keras.api.callbacks import Callback
from keras.api.utils import Progbar
from optuna.trial import Trial


class ProgbarWithoutMetrics(Callback):

    def __init__(self, trial_id):
        super().__init__()
        self.trial_id = trial_id

    def on_epoch_begin(self, epoch, logs=None):
        print(f"=========== START OF EPOCH {epoch} (Trial {self.trial_id}) ===========")
        self.progbar = Progbar(target=self.params['steps'])

    def on_batch_end(self, batch, logs=None):
        self.progbar.update(batch + 1)

    def on_epoch_end(self, epoch, logs=None):
        self.progbar.update(self.params['steps'], finalize=True)
        print(f"===========  END OF EPOCH {epoch} (Trial {self.trial_id}) ===========")


class SaveModelCallback(Callback):

    def __init__(self, trial: Trial, file_name_formatter, model_name, regime):
        super().__init__()
        self.trial_id = trial.number
        self.file_name_formatter = file_name_formatter
        self.model_name = model_name
        self.regime = regime

    def on_epoch_end(self, epoch, logs=None):
        file_name = self.file_name_formatter(
            f"trial_{self.trial_id}_epoch_{epoch}_{self.model_name}_{self.regime.name}.keras")
        self.model.save(file_name)


class SaveMetricCallback(Callback):

    def __init__(self, trial: Trial, file_name: str, lock: Lock, metric_columns, regime):
        super().__init__()
        self.trial_id = trial.number
        self.file_name = file_name
        self.lock = lock
        self.metrics = metric_columns
        self.regime = regime

    def on_epoch_end(self, epoch, logs=None):
        metrics = ",".join([str(logs[metric_name]) for metric_name in self.metrics])
        with self.lock:
            with open(self.file_name, "a") as file:
                file.write(
                    f"{self.trial_id},{epoch},{self.regime.name},{self.regime.value},{metrics}\n"
                )



class PercentageEarlyStopCallback(Callback):
    def __init__(self, trial_id, monitor, min_delta=0.001, verbose=1, minimize=True, stop_patience=3):
        super().__init__()
        self.monitor = monitor
        self.min_delta = min_delta
        self.verbose = verbose
        self.prev_value = None
        self.trial_id = trial_id
        self.minimize = minimize
        self.stop_patience = stop_patience
        self.should_stop_since = 0
        self.should_stop_in_current_epoch = False

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        current_value = logs.get(self.monitor)

        self.should_stop_in_current_epoch = False

        if current_value is None:
            if self.verbose:
                print(f"Warning: Metric '{self.monitor}' is not available in logs (Trial {self.trial_id}).")
            return

        if self.prev_value is not None:
            # Berechne die relative Änderung
            relative_change = (self.prev_value - current_value) / abs(self.prev_value + 1E-8)

            if self.verbose:
                print(
                    f"Epoch {epoch}: relative change in {self.monitor} = {relative_change:.5f} (Trial {self.trial_id})")

            if self.minimize:
                if current_value > self.prev_value:
                    self._stop_training(relative_change, direction_change=True, current_value=current_value)
            else:
                if current_value < self.prev_value:
                    self._stop_training(relative_change, direction_change=True, current_value=current_value)

            if abs(relative_change) < self.min_delta:
                self._stop_training(relative_change)

        if not self.should_stop_in_current_epoch:
            self.should_stop_since = 0
        self.prev_value = current_value

    def _stop_training(self, relative_change, direction_change=False, current_value=0):
        self.should_stop_since = self.should_stop_since + 1
        self.should_stop_in_current_epoch = True
        if self.should_stop_since < self.stop_patience:
            if self.verbose:
                print(
                    f"Should stop training, but waiting for better performance for {self.stop_patience - self.should_stop_since} Epochs (Trial {self.trial_id})")
            return
        if self.verbose:
            if direction_change:
                print(
                    f"Stopping training: {self.monitor} should {'decrease' if self.minimize else 'increase'} in each period, but changed from {self.prev_value} to {current_value}")
            else:
                print(
                    f"Stopping training: {self.monitor} improved {relative_change * 100:.2f}%, which is less than {self.min_delta * 100:.2f}% (Trial {self.trial_id})")

        self.model.stop_training = True
