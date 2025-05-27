from keras.api.callbacks import Callback
from keras.api.models import Model, clone_model
from torch import device

from zpython.training.data_set import RegimeDataLoader
from zpython.util.model_data_creator import ModelMarketRegime


def clone(model: Model):
    new_model = clone_model(model)
    new_model.compile(
        optimizer=type(model.optimizer).from_config(model.optimizer.get_config()),
        loss=model.loss,
        metrics=model.metrics,
    )
    return new_model


class ModelProvider:

    def __init__(self, provider_fn):
        self.provider_fn = provider_fn

    def get(self, input_dimension):
        return self.provider_fn(input_dimension)


class RegimeModel:

    def __init__(self, model_provider: ModelProvider, input_dimensions: dict[ModelMarketRegime, int]):
        self.regime_models = {regime: model_provider.get(input_dimensions[regime]) for regime in
                              input_dimensions.keys()}

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
