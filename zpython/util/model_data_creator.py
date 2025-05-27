from enum import Enum

import numpy as np
import pandas as pd
from tqdm import tqdm

from zpython.util.indicator_creator import create_indicators
from zpython.util.market_regime import MarketRegime, MarketRegimeDetector, market_regime_to_number


class ModelMarketRegime(Enum):
    UP_LOW_VOLA_033 = 1
    UP_LOW_VOLA_066 = 2
    UP_LOW_VOLA_1 = 3
    UP_HIGH_VOLA_033 = 4
    UP_HIGH_VOLA_066 = 5
    UP_HIGH_VOLA_1 = 6
    SIDE_LOW_VOLA_033 = 7
    SIDE_LOW_VOLA_066 = 8
    SIDE_LOW_VOLA_1 = 9
    SIDE_HIGH_VOLA_033 = 10
    SIDE_HIGH_VOLA_066 = 11
    SIDE_HIGH_VOLA_1 = 12
    DOWN_LOW_VOLA_033 = 13
    DOWN_LOW_VOLA_066 = 14
    DOWN_LOW_VOLA_1 = 15
    DOWN_HIGH_VOLA_033 = 16
    DOWN_HIGH_VOLA_066 = 17
    DOWN_HIGH_VOLA_1 = 18


def model_market_regime(regime: MarketRegime, quantile: float) -> ModelMarketRegime:
    if quantile <= 0.33:
        suffix = "033"
    elif quantile <= 0.66:
        suffix = "066"
    else:
        suffix = "1"

    regime_name = regime.name  # z.B. "UP_LOW_VOLA"
    enum_name = f"{regime_name}_{suffix}"  # z.B. "UP_LOW_VOLA_033"

    return ModelMarketRegime[enum_name]


def _model_market_regime_estimator(counts, regimes):
    all_regimes = list(MarketRegime)
    quantiles = {}
    quantil_values = [0.33, 0.66, 1]
    for r in all_regimes:
        quantiles[r] = np.array([
            np.quantile(counts[regimes == r.value].values, q) for q in quantil_values
        ])

    def find_model_regime(last_regime, regime_duration):
        q = quantiles[last_regime]
        idxs = np.argwhere(q > regime_duration)
        if len(idxs) == 0:
            return model_market_regime(last_regime, 1)

        return model_market_regime(last_regime, quantil_values[idxs[0][0]])

    return find_model_regime


def get_model_data_by_regime(data_read_function, input_length, output_length, regime_detector) -> \
        tuple[dict[ModelMarketRegime, list[pd.DataFrame]], pd.DataFrame, MarketRegimeDetector]:
    # Alle Daten einlesen
    data, regime_detector = create_indicators(data_read_function, regime_detector=regime_detector)
    # Regimes extrahieren und umwandeln
    regimes_non_number = data["regime"]
    regimes = data["regime"].apply(market_regime_to_number)
    data["regime"] = regimes
    # Dauer der Regimes berechnen
    group = (regimes != regimes.shift()).cumsum()
    counts = regimes.groupby(group).cumcount() + 1
    model_market_regime_estimator = _model_market_regime_estimator(counts, regimes)

    slices = {r: [] for r in list(ModelMarketRegime)}
    input_start_shift = pd.Timedelta(minutes=input_length - 1)
    output_end_shift = pd.Timedelta(minutes=output_length)
    expected_len = input_length + output_length

    for idx in tqdm(data.index.values, "Slicing data in regimes"):
        raw_window = data.loc[idx - input_start_shift:idx + output_end_shift]
        window = raw_window.dropna()
        if len(window) != expected_len or len(window) != len(raw_window):
            continue

        current_regime = regimes_non_number.loc[idx]
        current_count = counts.loc[idx]
        current_model_market_regime = model_market_regime_estimator(current_regime, current_count)
        slices[current_model_market_regime].append(window)

    return slices, data, regime_detector
