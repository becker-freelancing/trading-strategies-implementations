from concurrent.futures import ThreadPoolExecutor
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


def get_model_data_for_regime(
        data_read_function,
        regime: ModelMarketRegime,
        input_length: int,
        output_length: int,
        regime_detector
) -> tuple[list[pd.DataFrame], pd.DataFrame, MarketRegimeDetector]:
    # Daten und Indikatoren laden
    data, regime_detector = create_indicators(data_read_function, regime_detector=regime_detector)

    # Regime zu numerischen Werten konvertieren
    regimes_non_number = data["regime"]
    data["regime"] = regimes = regimes_non_number.apply(market_regime_to_number)

    # Dauer jedes Regime-Zustands berechnen
    regime_groups = (regimes != regimes.shift()).cumsum()
    regime_durations = regimes.groupby(regime_groups).cumcount() + 1

    # Regime-Schätzer vorbereiten
    regime_estimator = _model_market_regime_estimator(regime_durations, regimes)

    # Zeitverschiebungen berechnen
    input_shift = pd.Timedelta(minutes=input_length - 1)
    output_shift = pd.Timedelta(minutes=output_length)
    window_length = input_length + output_length

    # Gültige Indizes bestimmen (nur die, bei denen ein vollständiges Fenster möglich ist)
    valid_idx = data.index[
        (data.index >= data.index[0] + input_shift) &
        (data.index <= data.index[-1] - output_shift)
        ]

    # Funktion zur Verarbeitung eines einzelnen Index
    def process_idx(idx):
        start = idx - input_shift
        end = idx + output_shift
        window = data.loc[start:end]

        if window.isnull().values.any() or len(window) != window_length:
            return None

        current_regime = regimes_non_number.loc[idx]
        current_duration = regime_durations.loc[idx]
        estimated_regime = regime_estimator(current_regime, current_duration)

        return window if estimated_regime == regime else None

    # Parallelisierte Verarbeitung
    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(process_idx, valid_idx), total=len(valid_idx), desc="Slicing data in regimes"))

    # Nur gültige Fenster zurückgeben
    slices = [r for r in results if r is not None]

    return slices, data, regime_detector
