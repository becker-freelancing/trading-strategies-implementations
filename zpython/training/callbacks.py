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
