import joblib
import numpy as np
import pandas as pd
import torch

from zpython.model.best_model_loader import load_best_models
from zpython.model.regime_model import RegimeLiveModel, LoadedModelProvider
from zpython.util.data_split import backtest_data
from zpython.util.model_market_regime import ModelMarketRegime
from zpython.util.path_util import from_relative_path


def _to_string(arr):
    return np.array2string(arr.values.reshape(1, -1)[0], formatter={'float_kind': lambda x: f"{x:.15f}"})


class ClassificationModelPredictor:

    def __init__(self, model: RegimeLiveModel, file_name: str):
        self.model = model
        self.file_name = file_name

    def _load_data(self) -> pd.DataFrame:
        return backtest_data()

    def _reshape(self, all_predictions: dict[ModelMarketRegime, list[tuple[pd.Timestamp, pd.DataFrame]]]):
        reshaped_data = []
        for regime, predictions in all_predictions.items():
            for time, prediction in predictions:
                data = {
                    "closeTime": time,
                    "regimeName": regime.name,
                    "regimeId": regime.value,
                    "prediction": _to_string(prediction)
                }
                reshaped_data.append(data)

        return pd.DataFrame(reshaped_data)

    def predict_all(self):
        data = self._load_data().iloc[:10000]
        self.model.to(torch.device("cuda"))
        self.model.summary()
        prediction = self.model.predict(data)
        reshaped = self._reshape(prediction)
        path = from_relative_path(f"prediction-bybit/{self.file_name}")
        reshaped.to_csv(path, index=False)


def main():
    BASE_PATH = "CLASSIFICATION_240_WITHOUT_PCA"
    best_models = load_best_models(f"models-bybit/{BASE_PATH}")
    model_provider = LoadedModelProvider(best_models)
    model_regime_detector = joblib.load(
        from_relative_path(f"data-bybit/a-model-regime_detector_{BASE_PATH}.dump"))
    regime_detector = joblib.load(from_relative_path(f"data-bybit/a-regime_detector_{BASE_PATH}.dump"))
    scaler = joblib.load(from_relative_path(f"data-bybit/a-scaler_{BASE_PATH}.dump"))
    model = RegimeLiveModel(model_provider, scaler, None, model_regime_detector, regime_detector, is_regression=False,
                            is_use_pca=False)
    predictor = ClassificationModelPredictor(model, f"BACKTEST_PREDICTION_{BASE_PATH}.csv")
    predictor.predict_all()


if __name__ == "__main__":
    main()
