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
                 model_regime_detector: ModelMarketRegimeDetector,
                 regime_detector: MarketRegimeDetector):
        super().__init__({regime: model_provider.get(regime) for regime in list(ModelMarketRegime)})
        self.scaler = scaler
        self.pca = pca
        self.regime_detector = regime_detector
        self.model_regime_detector = model_regime_detector

    def predict(self, x: pd.DataFrame):
        x, _ = create_indicators(regime_detector=self.regime_detector,
                                 data=x)

        regimes_non_number = x["regime"]
        x["regime"] = regimes = regimes_non_number.apply(market_regime_to_number)

        # Dauer jedes Regime-Zustands berechnen
        regime_groups = (regimes != regimes.shift()).cumsum()
        regime_durations = regimes.groupby(regime_groups).cumcount() + 1
        market_model_regime = self.model_regime_detector.transform(regimes_non_number.iloc[-1],
                                                                   regime_durations.iloc[-1])

        x = self.scaler.transform([x], market_model_regime)
        x = self.pca.transform(x, market_model_regime)[0]

        model = self.regime_models[market_model_regime]
        return model.predict(x)
