import warnings

from zpython.model.regime_model import ModelProvider, RegimeTrainModel
from zpython.util.model_data_creator import ModelMarketRegime
from zpython.util.model_market_regime import ModelMarketRegimeDetector
from zpython.util.regime_pca import MarketRegimePCA
from zpython.util.regime_scaler import MarketRegimeScaler

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
import torch
from keras.api.callbacks import Callback
from optuna.trial import Trial

from zpython.training.optuna_env_provider import get_optuna_storage_url, get_optuna_study_name
from zpython.util.path_util import from_relative_path
import platform

from zpython.training.callbacks import ProgbarWithoutMetrics, SaveModelCallback, PercentageEarlyStopCallback
from zpython.training.train_util import get_device, run_study_for_model
from zpython.training.data_set import LazyTrainTensorDataSet, LazyValidationTensorDataSet, RegimeDataLoader
from zpython.util.market_regime import MarketRegimeDetector


def _get_max_epochs_to_train() -> int:
    return 20


def _get_optuna_optimization_metric_name() -> str:
    return "val_loss"


def _get_optuna_optimization_metric_direction() -> str:
    return "minimize"


def _get_optuna_processes() -> int:
    if "Win" in platform.system() or "win" in platform.system():
        return 1
    return 1


def _get_optuna_trials() -> int:
    return 30


def _tensor_data_path(idx, regime: ModelMarketRegime, data_selector: str, train=True):
    if train:
        return from_relative_path(f"data-bybit/{idx}_ETHUSDT_1_TRAIN_{data_selector}_{regime.name}.pt")
    else:
        return from_relative_path(f"data-bybit/{idx}_ETHUSDT_1_VAL_{data_selector}_{regime.name}.pt")


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
        self.regime_detector = None
        self.regime_pca = None
        self.model_regime_detector = None

    @abstractmethod
    def _get_max_input_length(self) -> int:
        pass

    @abstractmethod
    def _get_train_data(self, regime: ModelMarketRegime) -> tuple[np.ndarray, np.ndarray]:
        pass

    @abstractmethod
    def _get_validation_data(self, regime: ModelMarketRegime) -> tuple[np.ndarray, np.ndarray]:
        pass

    @abstractmethod
    def _get_metrics(self) -> list:
        pass

    @abstractmethod
    def _get_custom_callbacks(self, trial: Trial, lock: Lock, regime: ModelMarketRegime) -> list[Callback]:
        pass

    @abstractmethod
    def _create_model(self, optuna_trial: Trial) -> tuple[ModelProvider, int, dict]:
        pass

    @abstractmethod
    def _get_optuna_trial_params(self) -> list[str]:
        pass

    @abstractmethod
    def _get_data_selector(self) -> str:
        pass

    def _get_file_path(self, relative_path):
        dir = f"{from_relative_path('models-bybit/')}{self._get_data_selector()}/{self._build_optuna_study_name()}"
        os.makedirs(dir, exist_ok=True)
        return dir + "/" + relative_path

    def _get_metric_file_path(self):
        return self._get_file_path(f"a-metrics_{self.model_name}.csv")

    def _get_trials_file_path(self):
        return self._get_file_path(f"a-trials_{self.model_name}.csv")

    def _save_scaler(self):
        scaler = self._get_scaler()
        path = from_relative_path(f"data-bybit/a-scaler_{self._get_data_selector()}.dump")
        joblib.dump(scaler, path)

    def _save_regime_detector(self):
        scaler = self._get_regime_detector()
        path = from_relative_path(f"data-bybit/a-regime_detector_{self._get_data_selector()}.dump")
        joblib.dump(scaler, path)

    def _save_model_regime_detector(self):
        scaler = self._get_model_regime_detector()
        path = from_relative_path(f"data-bybit/a-model-regime_detector_{self._get_data_selector()}.dump")
        joblib.dump(scaler, path)

    def _save_pca(self):
        scaler = self._get_regime_pca()
        path = from_relative_path(f"data-bybit/a-regime_pca_{self._get_data_selector()}.dump")
        joblib.dump(scaler, path)

    def _get_callbacks(self, trial: Trial, lock: Lock, regime: ModelMarketRegime):
        custom_callbacks = self._get_custom_callbacks(trial, lock, regime)
        custom_callbacks.append(
            PercentageEarlyStopCallback(trial.number, monitor='val_loss')
        )
        custom_callbacks.append(ProgbarWithoutMetrics(trial.number))
        custom_callbacks.append(SaveModelCallback(trial, self._get_file_path, self.model_name, regime))
        return custom_callbacks

    def _get_scaler(self):
        if self.scaler is None:
            self.scaler = MarketRegimeScaler()

        return self.scaler

    def _get_regime_detector(self):
        if not self.regime_detector:
            self.regime_detector = MarketRegimeDetector()

        return self.regime_detector

    def _get_model_regime_detector(self):
        if not self.model_regime_detector:
            self.model_regime_detector = ModelMarketRegimeDetector()

        return self.model_regime_detector

    def _get_regime_pca(self):
        if not self.regime_pca:
            self.regime_pca = MarketRegimePCA(0.8)

        return self.regime_pca


    def _prepare_metrics_file(self):
        file_name = self._get_metric_file_path()
        if os.path.exists(file_name):
            return
        line_content = self._get_metric_columns()
        line = ",".join(line_content)
        with open(file_name, "w") as file:
            file.write(f"trial,epoch,regime_name,regime_id,{line}\n")

    def _get_metric_columns(self):
        if self.header_content is None:
            self.header_content = ["loss", "val_loss"] + [metric.name for metric in self._get_metrics()]
            self.header_content.extend([f"val_{metric.name}" for metric in self._get_metrics()])
        return self.header_content

    def _prepare_environment(self):
        print("Preparing environment...")
        path = self._get_file_path("")
        print("Working in directory: ", path)
        self._get_train_validation_data(self._get_max_input_length(), regime=ModelMarketRegime.UP_LOW_VOLA_033)
        self._prepare_metrics_file()
        self._prepare_params_file()

    def _prepare_params_file(self):
        path = self._get_trials_file_path()
        if os.path.exists(path):
            return
        with open(path, "w") as file:
            params = ",".join(self._get_optuna_trial_params())
            shapes = [
                [f"X_train_{regime}_shape", f"Y_train_{regime}_shape", f"X_val_{regime}_shape", f"Y_val_{regime}_shape"]
                for regime in list(ModelMarketRegime)]
            shapes = [shape for sublist in shapes for shape in sublist]
            shapes = ",".join(shapes)
            file.write(f"trial,{params},{shapes}\n")

    def _save_trial_params(self, trial_id, params, data_providers):
        if len(params) != len(self._get_optuna_trial_params()):
            raise Exception(
                f"Actual Params contain different params than expected.\n\tExpected: {self._get_optuna_trial_params()}\n\tActual:  {params.keys()}")
        with self.trials_lock:
            params_line = ",".join([str(params[key]) for key in self._get_optuna_trial_params()])
            shapes = [[f"'{train.feature_shape()}'", f"'{train.label_shape()}'", f"'{val.feature_shape()}'",
                       f"'{val.label_shape()}'"] for train, val in data_providers]
            shapes = [shape for sublist in shapes for shape in sublist]
            shapes = ",".join(shapes)
            line = f"{trial_id},{params_line},{shapes}\n"
            with open(self._get_trials_file_path(), "a") as file:
                file.write(line)



    def _create_objective(self, optuna_trial: Trial):

        model_provider, input_length, params = self._create_model(optuna_trial)

        data_providers = [self._get_train_validation_data(input_length, regime) for regime in list(ModelMarketRegime)]

        input_dimensions = {provider[0].regime: provider[0].feature_shape()[2] for provider in data_providers}
        model = RegimeTrainModel(model_provider=model_provider, input_dimensions=input_dimensions)

        self._save_trial_params(optuna_trial.number, params, data_providers)

        model.to(get_device())

        self.print_train_env(data_providers, model)

        for train_provider, val_provider in data_providers:
            model.fit(
                x=train_provider,
                validation_data=val_provider,
                epochs=_get_max_epochs_to_train(),
                callbacks=self._get_callbacks(optuna_trial, self.metrics_lock, train_provider.regime),
                verbose=0
            )

        score = model.evaluate(data_providers[0][1], verbose=0, return_dict=True)  # Todo
        return score["loss"]

    def print_train_env(self, data_providers, model):
        with self.trials_lock:
            print(f"Summary:\n{model.summary()}")
            for train_provider, val_provider in data_providers:
                print(
                    f"Data Shape for regime {train_provider.regime}: X_train {train_provider.feature_shape()}\tY_train {train_provider.label_shape()}\tX_valid {val_provider.feature_shape()}\tY_valid {val_provider.label_shape()}")

    def _create_train_val_data_tensor(self, chunk_size=15000):
        regimes = list(ModelMarketRegime)

        for regime in regimes:
            x_train, y_train = self._get_train_data(regime)
            i = -1
            for chunk in tqdm(range(0, len(x_train), chunk_size), f"Writing train tensors for regime {regime.name}"):
                i += 1
                torch.save((x_train[chunk:chunk + chunk_size], y_train[chunk:chunk + chunk_size]),
                           _tensor_data_path(i, regime, self._get_data_selector(), True))

        self._save_scaler()
        self._save_regime_detector()
        self._save_pca()
        self._save_model_regime_detector()

        for regime in regimes:
            x_val, y_val = self._get_validation_data(regime)
            i = -1
            for chunk in tqdm(range(0, len(x_val), chunk_size), f"Writing val tensors for regime {regime.name}"):
                i += 1
                torch.save((x_val[chunk:chunk + chunk_size], y_val[chunk:chunk + chunk_size]),
                           _tensor_data_path(i, regime, self._get_data_selector(), False))

    def _create_train_val_data_loader_provider(self, input_length, batch_size, val_data_size,
                                               regime: ModelMarketRegime):
        print("Creating train and validation data loader...")
        tensor_data_path = _tensor_data_path(0, regime, self._get_data_selector())
        if not os.path.exists(tensor_data_path):
            self._create_train_val_data_tensor()

        def train_data_loader():
            train_data_set = LazyTrainTensorDataSet(_tensor_data_path, input_length, regime, self._get_data_selector(),
                                                    None)
            return RegimeDataLoader(train_data_set, batch_size=batch_size, shuffle=False)

        def val_data_loader():
            val_data_set = LazyValidationTensorDataSet(_tensor_data_path, input_length, regime,
                                                       self._get_data_selector(), val_data_size)
            return RegimeDataLoader(val_data_set, batch_size=batch_size, shuffle=False)

        return train_data_loader, val_data_loader

    def _get_train_validation_data(self, input_length, regime, val_data_size=210111) -> tuple[
        RegimeDataLoader, RegimeDataLoader]:
        train_data_loader_provider, val_data_loader_provider = self._create_train_val_data_loader_provider(input_length,
                                                                                                           batch_size=256,
                                                                                                           val_data_size=val_data_size,
                                                                                                           regime=regime)
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
        study.optimize(self._create_objective, n_trials=ceil(_get_optuna_trials() / _get_optuna_processes()))


    def train_model(self):
        self._prepare_environment()

        self.study_storage = get_optuna_storage_url()
        study = optuna.create_study(direction=_get_optuna_optimization_metric_direction(),
                                    storage=self.study_storage,
                                    load_if_exists=True,
                                    study_name=self._build_optuna_study_name())

        self.metrics_lock = Lock()
        self.trials_lock = Lock()

        processes = []
        for _ in range(_get_optuna_processes()):
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
