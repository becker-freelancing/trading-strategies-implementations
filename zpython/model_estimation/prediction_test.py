from zpython.model.best_model_loader import load_best_models
from zpython.model.regime_model import LoadedModelProvider, RegimeLiveModel

models = load_best_models("modely-bybit/SEQUENCE_PREDICTION")

provider = LoadedModelProvider(models)
model = RegimeLiveModel(provider)  # TODO
