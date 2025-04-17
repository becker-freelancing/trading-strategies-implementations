import os
import shutil
import threading
from abc import abstractmethod
from datetime import datetime
from math import ceil
from threading import Lock

import joblib
import numpy as np
import optuna
import pandas as pd
import torch
from keras.api.callbacks import Callback
from keras.api.callbacks import EarlyStopping
from keras.api.models import Model
from keras.api.utils import Progbar
from optuna.trial import Trial

from zpython.indicators.indicator_creator import create_indicators
from zpython.training.optuna_env_provider import get_optuna_storage_url
from zpython.util.data_split import validation_data
from zpython.util.path_util import from_relative_path


class ProgbarWithoutMetrics(Callback):
    def on_epoch_begin(self, epoch, logs=None):
        print(f"=========== START OF EPOCH {epoch} ===========")
        self.progbar = Progbar(target=self.params['steps'])

    def on_batch_end(self, batch, logs=None):
        self.progbar.update(batch + 1)

    def on_epoch_end(self, epoch, logs=None):
        self.progbar.update(self.params['steps'], finalize=True)
        print(f"===========  END OF EPOCH {epoch}  ===========")


class SaveModelCallback(Callback):

    def __init__(self, trial: Trial, file_name_formatter, model_name):
        super().__init__()
        self.trial_id = trial.number
        self.file_name_formatter = file_name_formatter
        self.model_name = model_name

    def on_epoch_end(self, epoch, logs=None):
        file_name = self.file_name_formatter(f"trial_{self.trial_id}_epoch_{epoch}_{self.model_name}.keras")
        self.model.save(file_name)


def clean_directory(path):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def to_tensor(data: np.ndarray):
    return torch.from_numpy(data).float().to(get_device())


def run_study_for_model(model_class, model_name, study_name, storage_url, x_train, y_train, x_val, y_val, metrics_lock,
                        trials_lock, header_content, trial_params_keys):
    trainer = model_class()
    trainer.model_name = model_name
    trainer.study_name = study_name
    trainer.study_storage = storage_url
    trainer.x_train = x_train
    trainer.y_train = y_train
    trainer.x_val = x_val
    trainer.y_val = y_val
    trainer.study_name = study_name
    trainer.metrics_lock = metrics_lock
    trainer.trials_lock = trials_lock
    trainer.header_content = header_content
    trainer.trial_params_keys = trial_params_keys
    trainer._run_study()

class ModelTrainer:

    def __init__(self, model_name: str, scaler_provider):
        self.model_name = model_name
        self.scaler_provider = scaler_provider
        self.scaler = None
        self.x_train = None
        self.y_train = None
        self.x_val = None
        self.y_val = None
        self.study_storage = None
        self.study_name = None
        self.metrics_lock = None
        self.trials_lock = None
        self.header_content = None
        self.trial_params_keys = None

    @abstractmethod
    def _get_max_input_length(self) -> int:
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
    def _get_custom_callbacks(self, trial: Trial, lock: Lock) -> list[Callback]:
        pass

    @abstractmethod
    def _create_model(self, optuna_trial: Trial) -> (Model, int, dict):
        pass

    @abstractmethod
    def _get_max_epochs_to_train(self) -> int:
        pass

    @abstractmethod
    def _get_optuna_optimization_metric_name(self) -> str:
        pass

    @abstractmethod
    def _get_optuna_optimization_metric_direction(self) -> str:
        pass

    @abstractmethod
    def _get_train_data_limit(self) -> int:
        pass

    @abstractmethod
    def _get_optuna_processes(self) -> int:
        return 3

    @abstractmethod
    def _get_optuna_trials(self) -> int:
        return 30

    @abstractmethod
    def _get_optuna_trial_params(self) -> list[str]:
        pass

    def _get_file_path(self, relative_path):
        dir = from_relative_path("models-bybit/") + self.model_name
        os.makedirs(dir, exist_ok=True)
        return dir + "/" + relative_path

    def _get_metric_file_path(self):
        return self._get_file_path(f"a-metrics_{self.model_name}.csv")

    def _get_trials_file_path(self):
        return self._get_file_path(f"a-trials_{self.model_name}.csv")

    def _save_scaler(self):
        scaler = self._get_scaler()
        path = self._get_file_path(f"a-scaler_{self.model_name}.scaler")
        joblib.dump(scaler, path)


    def _limit_data(self, data):
        limit = self._get_train_data_limit()
        if limit is not None:
            return data[len(data) - limit:]
        return data

    def _get_callbacks(self, trial: Trial, lock: Lock):
        custom_callbacks = self._get_custom_callbacks(trial, lock)
        custom_callbacks.append(
            EarlyStopping(monitor='val_loss',
                          patience=5)
        )
        custom_callbacks.append(ProgbarWithoutMetrics())
        custom_callbacks.append(SaveModelCallback(trial, self._get_file_path, self.model_name))
        return custom_callbacks

    def _get_scaler(self):
        if self.scaler is None:
            self.scaler = self.scaler_provider()

        return self.scaler

    def _create_unsplited_data(self, train_data=True):
        if train_data:
            data = create_indicators()
            data = pd.DataFrame(self._get_scaler().fit_transform(data), columns=data.columns, index=data.index)
            self._save_scaler()
            return data
        else:
            data = create_indicators(validation_data)
            data = pd.DataFrame(self._get_scaler().transform(data), columns=data.columns, index=data.index)
            return data

    def _prepare_metrics_file(self):
        file_name = self._get_metric_file_path()
        line_content = self._get_metric_columns()
        line = ",".join(line_content)
        with open(file_name, "w") as file:
            file.write(f"trial,epoch,{line}\n")

    def _get_metric_columns(self):
        if self.header_content is None:
            self.header_content = [metric.name for metric in self._get_metrics()]
            self.header_content.extend([f"val_{metric.name}" for metric in self._get_metrics()])
        return self.header_content

    def _prepare_environment(self):
        clean_directory(self._get_file_path(""))
        self._get_train_validation_data(self._get_max_input_length())
        self._prepare_metrics_file()
        self._prepare_params_file()

    def _prepare_params_file(self, ):
        with open(self._get_trials_file_path(), "w") as file:
            line = ",".join(self._get_optuna_trial_params())
            file.write(f"trial,x_train_shape,y_train_shape,x_val_shape,y_val_shape,{line}\n")

    def _save_trial_params(self, trial_id, params, x_train_shape, y_train_shape, x_val_shape, y_val_shape):
        with self.trials_lock:
            line = ",".join([str(params[key]) for key in self._get_optuna_trial_params()])
            line = f"{trial_id},{x_train_shape},{y_train_shape},{x_val_shape},{y_val_shape},{line}\n"
            with open(self._get_trials_file_path(), "a") as file:
                file.write(line)



    def _create_objective(self, optuna_trial: Trial):

        model, input_length, params = self._create_model(optuna_trial)

        x_train, x_val, y_train, y_val = self._get_train_validation_data(input_length)
        with self.trials_lock:
            print(f"Summary:\n{model.summary()}")
            print(f"X_Train Shape: {x_train.shape}")
            print(f"X_Train Device: {x_train.device}")
            print(f"Y_Train Shape: {y_train.shape}")
            print(f"Y_Train Device: {y_train.device}")
            print(f"X_Valid Shape: {x_val.shape}")
            print(f"X_Valid Device: {x_val.device}")
            print(f"Y_Valid Shape: {y_val.shape}")
            print(f"Y_Valid Device: {y_val.device}")

        self._save_trial_params(optuna_trial.number, params, x_train.shape, y_train.shape, x_val.shape, y_val.shape)

        model.to(get_device())

        print("Model Device:", next(model.parameters()).device)

        model.fit(
            x=x_train,
            y=y_train,
            validation_data=(x_val, y_val),
            epochs=self._get_max_epochs_to_train(),
            batch_size=64,  # TODO: Batch-Size auch mit optuna verwalten -> Hyperparameter
            callbacks=self._get_callbacks(optuna_trial, self.metrics_lock),
            verbose=0,
            validation_batch_size=64
        )

        score = model.evaluate(x_val, y_val, verbose=0)
        return score[1]

    def _get_train_validation_data(self, input_length):
        if self.x_train is None:
            x_train, y_train = self._get_train_data()
            self.x_train = to_tensor(self._limit_data(x_train))
            self.y_train = to_tensor(self._limit_data(y_train))
            x_val, y_val = self._get_validation_data()
            self.x_val = to_tensor(x_val)
            self.y_val = to_tensor(y_val)

        return self.x_train[:, :input_length, :], self.x_val[:, :input_length, :], self.y_train, self.y_val

    def _build_optuna_study_name(self):
        if self.study_name is None:
            time = str(datetime.now()).replace(" ", "_").replace(":", "-")[:19]
            self.study_name = f"{self.model_name}_{time}"
        return self.study_name

    def _run_study(self):
        study = optuna.load_study(
            study_name=self.study_name,
            storage=self.study_storage
        )
        study.optimize(self._create_objective, n_trials=ceil(self._get_optuna_trials() / self._get_optuna_processes()))


    def train_model(self):
        self._prepare_environment()

        self.study_storage = get_optuna_storage_url()
        study = optuna.create_study(direction=self._get_optuna_optimization_metric_direction(),
                                    storage=self.study_storage,
                                    load_if_exists=True,
                                    study_name=self._build_optuna_study_name())

        self.metrics_lock = Lock()
        self.trials_lock = Lock()

        processes = []
        for _ in range(self._get_optuna_processes()):
            p = threading.Thread(
                target=run_study_for_model,
                args=(self.__class__,
                      self.model_name,
                      self.study_name,
                      self.study_storage,
                      self.x_train,
                      self.y_train,
                      self.x_val,
                      self.y_val,
                      self.metrics_lock,
                      self.trials_lock,
                      self.header_content,
                      self.trial_params_keys)
            )
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print(study)
        print("Best trial:")
        trial = study.best_trial

        print("  Value: {}".format(trial.value))

        print("  Params: ")
        for key, value in trial.params.items():
            print("    {}: {}".format(key, value))
