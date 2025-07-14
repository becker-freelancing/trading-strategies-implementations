from datetime import datetime

import joblib
import pandas as pd
from japy.japy_function import japy_function

from zpython.model.best_model_loader_classification import load_best_classification_models
from zpython.model.regime_model import RegimeLiveModel, LoadedModelProvider
from zpython.util.model_market_regime import ModelMarketRegime
from zpython.util.path_util import from_relative_path


class Cache:
    best_models = load_best_classification_models("models-bybit/CLASSIFICATION_240")
    model_provider = LoadedModelProvider(best_models)
    pca = joblib.load(from_relative_path("data-bybit/a-regime_pca_CLASSIFICATION_240.dump"))
    scaler = joblib.load(from_relative_path("data-bybit/a-scaler_CLASSIFICATION_240.dump"))
    model = RegimeLiveModel(model_provider, scaler, pca, is_regression=False)


@japy_function
def predict_classification(regime_id: int, data: dict[str, list[float]]):
    print(f"{datetime.now()} - Start predicting ")
    regime = ModelMarketRegime(regime_id)
    x = pd.DataFrame(data=data)
    prediction = Cache.model.predict_with_data(x, regime)
    print(f"{datetime.now()} - End Prediction: {prediction}")
    return list(prediction.values.astype(float).reshape(1, -1)[0])


@japy_function
def required_input_lengths_classification() -> dict[int, int]:
    return Cache.model.input_lengths
