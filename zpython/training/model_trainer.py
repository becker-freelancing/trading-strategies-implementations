import warnings

# Nur das spezifische FutureWarning von torch.load filtern
warnings.filterwarnings(
    "ignore",
    category=FutureWarning
)

import os
import threading
from abc import abstractmethod
from datetime import datetime
from math import ceil
from threading import Lock

from tqdm import tqdm
import joblib
import numpy as np
import optuna
import pandas as pd
import torch
from keras.api.callbacks import Callback
from keras.api.models import Model
from optuna.trial import Trial
from torch.utils.data import DataLoader

from zpython.indicators.indicator_creator import create_indicators
from zpython.training.optuna_env_provider import get_optuna_storage_url, get_optuna_study_name
from zpython.util.data_split import validation_data
from zpython.util.path_util import from_relative_path
import platform

from zpython.training.callbacks import ProgbarWithoutMetrics, SaveModelCallback, PercentageEarlyStopCallback
from zpython.training.train_util import get_device, run_study_for_model
from zpython.training.data_set import LazyTrainTensorDataSet, LazyValidationTensorDataSet

class ModelTrainer:

    def __init__(self, model_name: str, scaler_provider):
        self.model_name = model_name
        self.scaler_provider = scaler_provider
        self.scaler = None
        self.study_storage = None
        self.study_name = get_optuna_study_name()
        self.metrics_lock = None
        self.trials_lock = None
        self.header_content = None
        self.trial_params_keys = None
        self.train_data_loader_provider = None
        self.val_data_loader_provider = None

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
    def _create_model(self, optuna_trial: Trial) -> tuple[Model, int, dict]:
        pass

    def _get_max_epochs_to_train(self) -> int:
        return 20

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
        if "Win" in platform.system() or "win" in platform.system():
            return 2
        return 10

    @abstractmethod
    def _get_optuna_trials(self) -> int:
        return 30

    @abstractmethod
    def _get_optuna_trial_params(self) -> list[str]:
        pass

    def _get_file_path(self, relative_path):
        dir = f"{from_relative_path('models-bybit/')}{self._build_optuna_study_name()}"
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
            PercentageEarlyStopCallback(trial.number, monitor='val_loss')
        )
        custom_callbacks.append(ProgbarWithoutMetrics(trial.number))
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
        if os.path.exists(file_name):
            return
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
        print("Preparing environment...")
        path = self._get_file_path("")
        print("Working in directory: ", path)
        self._get_train_validation_data(self._get_max_input_length())
        self._prepare_metrics_file()
        self._prepare_params_file()

    def _prepare_params_file(self):
        path = self._get_trials_file_path()
        if os.path.exists(path):
            return
        with open(path, "w") as file:
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

        train_data_provider, val_data_provider = self._get_train_validation_data(input_length)

        train_feature_shape = train_data_provider.dataset.feature_shape()
        train_label_shape = train_data_provider.dataset.label_shape()
        val_feature_shape = val_data_provider.dataset.feature_shape()
        val_label_shape = val_data_provider.dataset.label_shape()


        self._save_trial_params(optuna_trial.number, params, train_feature_shape, train_label_shape, val_feature_shape,
                                val_label_shape)

        model.to(get_device())

        with self.trials_lock:
            print(f"Summary:\n{model.summary()}")
            print(f"X_Train Shape: {train_feature_shape}")
            print(f"Y_Train Shape: {train_label_shape}")
            print(f"X_Valid Shape: {val_feature_shape}")
            print(f"Y_Valid Shape: {val_label_shape}")
            print("Model Device:", next(model.parameters()).device)

        model.fit(
            x=train_data_provider,
            validation_data=val_data_provider,
            epochs=self._get_max_epochs_to_train(),
            callbacks=self._get_callbacks(optuna_trial, self.metrics_lock),
            verbose=0
        )

        score = model.evaluate(val_data_provider, verbose=0)
        return score[1]

    def _create_train_val_data_tensor(self, chunk_size=15000):
        x_train, y_train = self._get_train_data()
        x_val, y_val = self._get_validation_data()
        i = -1
        for chunk in tqdm(range(0, len(x_train), chunk_size), "Writing train tensors"):
            i += 1
            torch.save((x_train[chunk:chunk + chunk_size], y_train[chunk:chunk + chunk_size]),
                       self._tensor_data_path(i, True))

        i = -1
        for chunk in tqdm(range(0, len(x_val), chunk_size), "Writing val tensors"):
            i += 1
            torch.save((x_val[chunk:chunk + chunk_size], y_val[chunk:chunk + chunk_size]),
                       self._tensor_data_path(i, False))

    def _create_train_val_data_loader_provider(self, input_length, batch_size):
        print("Creating train and validation data loader...")
        tensor_data_path = self._tensor_data_path(0)
        if not os.path.exists(tensor_data_path):
            self._create_train_val_data_tensor()

        def train_data_loader():
            train_data_set = LazyTrainTensorDataSet(self._tensor_data_path, input_length, self._get_train_data_limit())
            return DataLoader(train_data_set, batch_size=batch_size, shuffle=False)

        def val_data_loader():
            val_data_set = LazyValidationTensorDataSet(self._tensor_data_path, input_length)
            return DataLoader(val_data_set, batch_size=batch_size, shuffle=False)

        return train_data_loader, val_data_loader

    def _tensor_data_path(self, idx, train=True):
        if train:
            return from_relative_path(f"data-bybit/{idx}_ETHUSDT_1_TRAIN.pt")
        else:
            return from_relative_path(f"data-bybit/{idx}_ETHUSDT_1_VAL.pt")

    def _get_train_validation_data(self, input_length):
        train_data_loader_provider, val_data_loader_provider = self._create_train_val_data_loader_provider(input_length,
                                                                                                           batch_size=256)
        return train_data_loader_provider(), val_data_loader_provider()

    def _build_optuna_study_name(self):
        if self.study_name is None:
            time = str(datetime.now()).replace(" ", "_").replace(":", "-")[:19]
            self.study_name = f"{self.model_name}_{time}"
        return self.study_name

    def _run_study(self):
        study = optuna.load_study(
            study_name=self._build_optuna_study_name(),
            storage=self.study_storage,

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
