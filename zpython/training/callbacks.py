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

    def __init__(self, trial: Trial, file_name_formatter, model_name):
        super().__init__()
        self.trial_id = trial.number
        self.file_name_formatter = file_name_formatter
        self.model_name = model_name

    def on_epoch_end(self, epoch, logs=None):
        file_name = self.file_name_formatter(f"trial_{self.trial_id}_epoch_{epoch}_{self.model_name}.keras")
        self.model.save(file_name)


class PercentageEarlyStopCallback(Callback):
    def __init__(self, trial_id, monitor, min_delta=0.001, verbose=1):
        super().__init__()
        self.monitor = monitor
        self.min_delta = min_delta
        self.verbose = verbose
        self.prev_value = None
        self.trial_id = trial_id

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        current_value = logs.get(self.monitor)

        if current_value is None:
            if self.verbose:
                print(f"Warning: Metric '{self.monitor}' is not available in logs (Trial {self.trial_id}).")
            return

        if self.prev_value is not None:
            # Berechne die relative Änderung
            relative_change = abs(self.prev_value - current_value) / self.prev_value

            if self.verbose:
                print(
                    f"Epoch {epoch}: relative change in {self.monitor} = {relative_change:.5f} (Trial {self.trial_id})")

            if relative_change < self.min_delta:
                if self.verbose:
                    print(
                        f"Stopping training: {self.monitor} improved less than {self.min_delta * 100:.2f}% (Trial {self.trial_id})")
                self.model.stop_training = True

        self.prev_value = current_value
