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
from zpython.util.path_util import from_relative_path

test_data = test_data()
BASE_PATH = "CLASSIFICATION_240"
best_models = load_best_models(f"models-bybit/{BASE_PATH}")
model_provider = LoadedModelProvider(best_models)
model_regime_detector = joblib.load(
    from_relative_path(f"data-bybit/a-model-regime_detector_{BASE_PATH}.dump"))
regime_detector = joblib.load(from_relative_path(f"data-bybit/a-regime_detector_{BASE_PATH}.dump"))
pca = joblib.load(from_relative_path(f"data-bybit/a-regime_pca_{BASE_PATH}.dump"))
scaler = joblib.load(from_relative_path(f"data-bybit/a-scaler_{BASE_PATH}.dump"))
model = RegimeModel({regime: model_provider.get(regime) for regime in list(ModelMarketRegime)})

input_lengths = {key.value: val.input_shape[1] for key, val in model.regime_models.items()}

x, _ = create_indicators(regime_detector=regime_detector,
                         data=test_data)
x = x[~x.index.duplicated(keep="first")]

regimes_non_number = x["regime"]
x["regime"] = regimes = regimes_non_number.apply(market_regime_to_number)

# Dauer jedes Regime-Zustands berechnen
regime_groups = (regimes != regimes.shift()).cumsum()
regime_durations = regimes.groupby(regime_groups).cumcount() + 1
for idx in x.index:
    regime = regimes_non_number[idx]
    duration = regime_durations[idx]
    model_regime = model_regime_detector.transform(regime, duration)
    x.loc[idx, "regime"] = model_regime.value
predict_times = pd.Series(x.index)
input_shifts = {key: pd.Timedelta(minutes=val) for key, val in input_lengths.items()}


def _transform_data(data: dict[ModelMarketRegime, list[tuple[pd.Timestamp, pd.DataFrame]]]) -> dict[
    ModelMarketRegime, list[tuple[pd.Timestamp, np.ndarray]]]:
    result = {}
    for regime, xs in data.items():
        keys = [x[0] for x in xs]
        values = [x[1] for x in xs]
        scaled = scaler.transform(values, regime)
        pca = pca.transform(scaled, regime)
        pca = [(k, v) for k, v in zip(keys, pca)]
        result[regime] = pca
    return result


def _slice_data_by_regime(x: pd.DataFrame, predict_times: pd.Series, regimes: pd.Series) -> dict[
    ModelMarketRegime, list[tuple[pd.Timestamp, np.ndarray]]]:
    time_shifts = regimes.apply(lambda regime: input_shifts[regime])
    start_times = predict_times - time_shifts + pd.Timedelta(minutes=1)
    results = {ModelMarketRegime(key): [] for key in input_lengths.keys()}
    for end_time in predict_times:
        start_time = start_times.loc[end_time]
        slice = x.loc[start_time:end_time]
        regime = regimes.loc[end_time]
        if input_lengths[regime] != len(slice):
            continue
        if np.isnan(slice.values).any():
            continue
        results[ModelMarketRegime(regime)].append((end_time, slice))
    results = _transform_data(results)
    return results


sliced_data = _slice_data_by_regime(x, predict_times, x["regime"])

model.to(torch.device("cuda"))
for regime, data in sliced_data.items():
    eval_model = model.regime_models[regime]
    evalution = eval_model.evaluate(x=data, return_dict=True)
    print(regime)
    print(evalution)
    print()
