import numpy as np
import pandas as pd
from keras.api.callbacks import Callback
from keras.api.models import Model
from torch import device

from zpython.training.data_set import RegimeDataLoader
from zpython.util.indicator_creator import create_indicators
from zpython.util.market_regime import MarketRegimeDetector
from zpython.util.market_regime import market_regime_to_number
from zpython.util.model_data_creator import ModelMarketRegime
from zpython.util.model_market_regime import ModelMarketRegimeDetector
from zpython.util.regime_pca import MarketRegimePCA
from zpython.util.regime_scaler import MarketRegimeScaler


class ModelProvider:

    def __init__(self, provider_fn):
        self.provider_fn = provider_fn

    def get(self, input_dimension):
        return self.provider_fn(input_dimension)


class LoadedModelProvider:
    def __init__(self, models: dict[ModelMarketRegime, Model]):
        self.models = models

    def get(self, regime: ModelMarketRegime) -> Model:
        return self.models[regime]

class RegimeModel:
    def __init__(self, regime_models: dict[ModelMarketRegime, Model]):
        self.regime_models = regime_models

    def to(self, to: device):
        for model in self.regime_models.values():
            model.to(to)

    def summary(self):
        print("=" * 50)
        print("~" + " " * 18 + "Regime-Model" + " " * 18 + "~")
        print("" + "~" * 50)
        for regime in self.regime_models.keys():
            print("~" + " " * 18 + f"Regime: {regime.name}")
            self.regime_models[regime].summary()
            print("" + "~" * 50)
        print("" + "=" * 50 + "\n" + "=" * 50)


class RegimeTrainModel(RegimeModel):
    def __init__(self, model_provider: ModelProvider, input_dimensions: dict[ModelMarketRegime, int]):
        super().__init__({regime: model_provider.get(input_dimensions[regime]) for regime in
                          input_dimensions.keys()})


    def fit(self, x: RegimeDataLoader, validation_data: RegimeDataLoader, epochs: int, callbacks: list[Callback],
            verbose=0):
        model = self.regime_models[x.regime]

        return model.fit(
            x=x,
            validation_data=validation_data,
            epochs=epochs,
            callbacks=callbacks,
            verbose=verbose
        )

    def evaluate(self, x: RegimeDataLoader, return_dict=True, verbose=0):
        model = self.regime_models[x.regime]

        return model.evaluate(
            x=x,
            return_dict=return_dict,
            verbose=verbose
        )


class RegimeLiveModel(RegimeModel):

    def __init__(self, model_provider: LoadedModelProvider, scaler: MarketRegimeScaler, pca: MarketRegimePCA,
                 model_regime_detector: ModelMarketRegimeDetector = None,
                 regime_detector: MarketRegimeDetector = None):
        super().__init__({regime: model_provider.get(regime) for regime in list(ModelMarketRegime)})
        self.scaler = scaler
        self.pca = pca
        self.regime_detector = regime_detector
        self.model_regime_detector = model_regime_detector
        self.input_lengths = {key.value: val.input_shape[1] for key, val in self.regime_models.items()}
        self.input_shifts = {key: pd.Timedelta(minutes=val) for key, val in self.input_lengths.items()}
        self.init_models()



    def _transform_data(self, data: dict[ModelMarketRegime, list[tuple[pd.Timestamp, pd.DataFrame]]]) -> dict[
        ModelMarketRegime, list[tuple[pd.Timestamp, np.ndarray]]]:
        result = {}
        for regime, xs in data.items():
            keys = [x[0] for x in xs]
            values = [x[1] for x in xs]
            scaled = self.scaler.transform(values, regime)
            pca = self.pca.transform(scaled, regime)
            pca = [(k, v) for k, v in zip(keys, pca)]
            result[regime] = pca
        return result

    def _slice_data_by_regime(self, x: pd.DataFrame, predict_times: pd.Series, regimes: pd.Series) -> dict[
        ModelMarketRegime, list[tuple[pd.Timestamp, np.ndarray]]]:
        time_shifts = regimes.apply(lambda regime: self.input_shifts[regime])
        start_times = predict_times - time_shifts + pd.Timedelta(minutes=1)
        results = {ModelMarketRegime(key): [] for key in self.input_lengths.keys()}
        for end_time in predict_times:
            start_time = start_times.loc[end_time]
            slice = x.loc[start_time:end_time]
            regime = regimes.loc[end_time]
            if self.input_lengths[regime] != len(slice):
                continue
            if np.isnan(slice.values).any():
                continue
            results[ModelMarketRegime(regime)].append((end_time, slice))
        results = self._transform_data(results)
        return results

    def init_models(self):
        for regime in self.regime_models.keys():
            input_length = self.input_lengths[regime.value]
            feature_names = self.scaler.scalers[regime].feature_names_in_
            x = pd.DataFrame(data=np.random.random((input_length, len(feature_names))), columns=feature_names)
            self.predict_with_data(x, regime)

    def predict_with_data(self, x: pd.DataFrame, regime: ModelMarketRegime) -> pd.DataFrame:
        x_scaled = self.scaler.transform([x], regime)
        x_reduced = self.pca.transform(x_scaled, regime)[0]
        x_reduced = np.expand_dims(x_reduced, axis=0)
        model = self.regime_models[regime]
        prediction = model.predict(x_reduced)[0]
        prediction = pd.DataFrame(prediction, columns=["logReturn_closeBid_1min"])
        inverse_transform = self.scaler.inverse_transform([prediction], regime)[0]
        return inverse_transform

    def predict(self, x: pd.DataFrame, predict_times: pd.Series = None) -> dict[
        ModelMarketRegime, list[tuple[pd.Timestamp, pd.DataFrame]]]:
        x, _ = create_indicators(regime_detector=self.regime_detector,
                                 data=x)
        x = x[~x.index.duplicated(keep="first")]

        if predict_times is None:
            predict_times = pd.Series(x.index)
        if not isinstance(predict_times.index, pd.DatetimeIndex):
            predict_times.index = pd.DatetimeIndex(data=predict_times.values)

        regimes_non_number = x["regime"]
        x["regime"] = regimes = regimes_non_number.apply(market_regime_to_number)

        # Dauer jedes Regime-Zustands berechnen
        regime_groups = (regimes != regimes.shift()).cumsum()
        regime_durations = regimes.groupby(regime_groups).cumcount() + 1
        for idx in x.index:
            regime = regimes_non_number[idx]
            duration = regime_durations[idx]
            model_regime = self.model_regime_detector.transform(regime, duration)
            x.loc[idx, "regime"] = model_regime.value

        sliced_data = self._slice_data_by_regime(x, predict_times, x["regime"])
        predicted = {}
        for regime, prediction_data in sliced_data.items():
            if len(prediction_data) == 0:
                predicted[regime] = []
                continue
            times = [v[0] for v in prediction_data]
            data = [v[1] for v in prediction_data]
            data = np.stack(data)
            prediction = self.regime_models[regime].predict(data)
            prediction = [pd.DataFrame(a, columns=["logReturn_closeBid_1min"]) for a in list(prediction)]
            transformed = self.scaler.inverse_transform(prediction, regime)
            predicted[regime] = list(zip(times, transformed))
        return predicted
