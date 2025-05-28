from zpython.model.regime_model import LoadedModelProvider, RegimeLiveModel
from zpython.model_estimation.prediction import load_best_models

models = load_best_models("modely-bybit/SEQUENCE_PREDICTION")

provider = LoadedModelProvider(models)
model = RegimeLiveModel(provider)  # TODO
