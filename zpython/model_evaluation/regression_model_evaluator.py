import joblib
import numpy as np
import pandas as pd
import torch

from zpython.model.best_model_loader import load_best_models
from zpython.model.regime_model import RegimeModel, LoadedModelProvider
from zpython.util.data_split import test_data
from zpython.util.indicator_creator import create_indicators
from zpython.util.market_regime import market_regime_to_number
from zpython.util.model_market_regime import ModelMarketRegime
from zpython.util.market_regime import market_regime_to_number
from zpython.util.path_util import from_relative_path
from zpython.util.model_data_creator import get_model_data_for_regime

#test_data = test_data().iloc[:10000]
BASE_PATH = "SEQUENCE_REGRESSION"
best_models = load_best_models(f"models-bybit/{BASE_PATH}")
model_provider = LoadedModelProvider(best_models)
model_regime_detector = joblib.load(
    from_relative_path(f"data-bybit/a-model-regime_detector_{BASE_PATH}.dump"))
regime_detector = joblib.load(from_relative_path(f"data-bybit/a-regime_detector_{BASE_PATH}.dump"))
pca_transformer = joblib.load(from_relative_path(f"data-bybit/a-regime_pca_{BASE_PATH}.dump"))
scaler = joblib.load(from_relative_path(f"data-bybit/a-scaler_{BASE_PATH}.dump"))
model = RegimeModel({regime: model_provider.get(regime) for regime in list(ModelMarketRegime)})
input_lengths = {key.value: val.input_shape[1] for key, val in model.regime_models.items()}


model.to(torch.device("cuda"))
for regime in list(ModelMarketRegime):
    try:
        input_length = input_lengths[regime.value]
        feature_names = scaler.scalers[regime].feature_names_in_
        eval_model = model.regime_models[regime]
        x = np.random.random((input_length, pca_transformer.pcas[regime].n_components_))
        x = np.expand_dims(x, axis=0)
        print(eval_model.summary())
        eval_model.predict(x)

        slices, complete_data, _, _ = get_model_data_for_regime(test_data, regime, input_lengths[regime.value], 30, regime_detector, model_regime_detector)
        target_col_idx = complete_data.columns.get_loc("logReturn_closeBid_1min")
        trans_slices = scaler.transform(slices, regime)
        red_slices = pca_transformer.transform(trans_slices, regime)

        input_data = np.stack([df[:input_length, :] for df in red_slices])
        output_data = np.stack([df.to_numpy()[:, target_col_idx].reshape(-1, 1)[input_length:, :] for df in slices])
        output_data = output_data.reshape(-1, output_data.shape[1])

        evalution = eval_model.evaluate(x=input_data, y=output_data, return_dict=True)
        print(regime)
        print(evalution)
        print()
    except Exception as e:
        print(regime)
        print(e)
