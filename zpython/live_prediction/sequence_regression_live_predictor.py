import joblib
import pandas as pd
from japy.japy_function import japy_function

from zpython.model.best_model_loader import load_best_models
from zpython.model.regime_model import RegimeLiveModel, LoadedModelProvider
from zpython.util.model_market_regime import ModelMarketRegime
from zpython.util.path_util import from_relative_path


class Cache:
    best_models = load_best_models("models-bybit/SEQUENCE_REGRESSION")
    model_provider = LoadedModelProvider(best_models)
    pca = joblib.load(from_relative_path("data-bybit/a-regime_pca_SEQUENCE_REGRESSION.dump"))
    scaler = joblib.load(from_relative_path("data-bybit/a-scaler_SEQUENCE_REGRESSION.dump"))
    model = RegimeLiveModel(model_provider, scaler, pca)


@japy_function
def predict(regime_id: int, data: dict[str, list[float]]):
    regime = ModelMarketRegime(regime_id)
    x = pd.DataFrame(data=data)
    prediction = Cache.model.predict_with_data(x, regime)
    return list(prediction["logReturn_closeBid_1min"].values)


@japy_function
def required_input_lengths() -> dict[int, int]:
    return Cache.model.input_lengths
