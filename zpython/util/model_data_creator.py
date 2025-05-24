import numpy as np
import pandas as pd
from tqdm import tqdm

from zpython.util.indicator_creator import create_indicators
from zpython.util.market_regime import MarketRegime, MarketRegimeDetector, market_regime_to_number


def get_model_data_by_regime(data_read_function, input_length, output_length, regime_detector) -> tuple[
    dict[MarketRegime, list[pd.DataFrame]], pd.DataFrame, MarketRegimeDetector]:
    data, regime_detector = create_indicators(data_read_function, regime_detector=regime_detector)
    data["regime"] = data["regime"].apply(market_regime_to_number)
    regimes = data["regime"]
    group = (regimes != regimes.shift()).cumsum()
    counts = regimes.groupby(group).cumcount() + 1

    slices = {market_regime_to_number(key): [] for key in list(MarketRegime)}
    indices = counts.index[counts >= output_length].tolist()

    idx_shift = pd.Timedelta(minutes=input_length + output_length - 1)
    expected_len = input_length + output_length
    for idx in tqdm(indices, "Slicing data in regimes"):
        start = idx - idx_shift
        window = data.loc[start:idx]

        if len(window) != expected_len:
            continue
        if np.isnan(window.to_numpy()).any():
            continue
        regime = window.iloc[-1]["regime"]
        slices[regime].append(window)

    result = {}
    for regime in slices.keys():
        result[MarketRegime(regime)] = slices[regime]
    return result, data, regime_detector
