from abc import abstractmethod

import numpy as np
import optuna
import pandas as pd
from keras.api.backend import clear_session
from keras.api.callbacks import Callback
from keras.api.callbacks import EarlyStopping
from keras.api.models import Model
from keras.api.utils import Progbar
from optuna.trial import Trial

from zpython.indicators.indicator_creator import create_indicators
from zpython.util.data_split import validation_data


class ProgbarWithoutMetrics(Callback):
    def on_epoch_begin(self, epoch, logs=None):
        print(f"=========== START OF EPOCH {epoch} ===========")
        self.progbar = Progbar(target=self.params['steps'])

    def on_batch_end(self, batch, logs=None):
        self.progbar.update(batch + 1)

    def on_epoch_end(self, epoch, logs=None):
        self.progbar.update(self.params['steps'], finalize=True)
        print(f"===========  END OF EPOCH {epoch}  ===========")


class ModelTrainer:

    def __init__(self, model_name: str, scaler_provider):
        self.model_name = model_name
        self.scaler_provider = scaler_provider
        self.scaler = None
        self.x_train = None
        self.y_train = None
        self.x_val = None
        self.y_val = None

    @abstractmethod
    def _get_input_length(self):
        pass

    @abstractmethod
    def _get_train_data(self) -> tuple[np.ndarray, np.ndarray]:
        pass

    @abstractmethod
    def _get_validation_data(self) -> tuple[np.ndarray, np.ndarray]:
        pass

    @abstractmethod
    def _get_metrics(self) -> list:
        pass

    @abstractmethod
    def _get_custom_epoch_end_callbacks(self) -> list[Callback]:
        pass

    @abstractmethod
    def _create_model(self, optuna_trial: Trial) -> Model:
        pass

    @abstractmethod
    def _get_max_epochs_to_train(self):
        pass

    @abstractmethod
    def _get_optuna_optimization_metric_name(self):
        pass

    @abstractmethod
    def _get_optuna_optimization_metric_direction(self):
        pass

    @abstractmethod
    def _get_train_data_limit(self):
        pass

    def _limit_data(self, data):
        limit = self._get_train_data_limit()
        if limit is not None:
            return data[len(data) - limit:]
        return data

    def _get_epoch_end_callbacks(self):
        custom_callbacks = self._get_custom_epoch_end_callbacks()
        custom_callbacks.append(
            EarlyStopping(monitor='val_loss',
                          patience=5)
        )
        custom_callbacks.append(ProgbarWithoutMetrics())
        return custom_callbacks

    def _get_scaler(self):
        if self.scaler is None:
            self.scaler = self.scaler_provider()

        return self.scaler

    def _create_unsplited_data(self, train_data=True):
        if train_data:
            data = create_indicators()
            data = pd.DataFrame(self._get_scaler().fit_transform(data), columns=data.columns, index=data.index)
            return data
        else:
            data = create_indicators(validation_data)
            data = pd.DataFrame(self._get_scaler().transform(data), columns=data.columns, index=data.index)
            return data

    def _create_objective(self, optuna_trial: Trial):
        clear_session()

        x_train, x_val, y_train, y_val = self._get_train_validation_data()

        model = self._create_model(optuna_trial)

        print(f"Summary:\n{model.summary()}")
        print(f"X_Train Shape: {x_train.shape}")
        print(f"Y_Train Shape: {y_train.shape}")
        print(f"X_Valid Shape: {x_val.shape}")
        print(f"Y_Valid Shape: {y_val.shape}")

        history = model.fit(
            x=x_train,
            y=y_train,
            validation_data=(x_val, y_val),
            epochs=self._get_max_epochs_to_train(),
            batch_size=64,  # TODO: Batch-Size auch mit optuna verwalten -> Hyperparameter
            callbacks=self._get_epoch_end_callbacks(),
            verbose=0,
            validation_batch_size=64
        )

        score = model.evaluate(x_val, y_val, verbose=0)
        return score[1]

    def _get_train_validation_data(self):
        if self.x_train is None:
            x_train, y_train = self._get_train_data()
            self.x_train = self._limit_data(x_train)
            self.y_train = self._limit_data(y_train)
            x_val, y_val = self._get_validation_data()
            self.x_val = self._limit_data(x_val)  # TODO: Remove
            self.y_val = self._limit_data(y_val)  # TODO: Remove
        return self.x_train, self.x_val, self.y_train, self.y_val

    def train_model(self):
        study = optuna.create_study(direction=self._get_optuna_optimization_metric_direction(),
                                    study_name=f"study_{self.model_name}")
        study.optimize(self._create_objective, n_trials=20)

        print(study)
        print("Best trial:")
        trial = study.best_trial

        print("  Value: {}".format(trial.value))

        print("  Params: ")
        for key, value in trial.params.items():
            print("    {}: {}".format(key, value))
