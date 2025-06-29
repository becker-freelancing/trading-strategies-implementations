from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from tqdm import tqdm

from zpython.util.indicator_creator import create_indicators
from zpython.util.market_regime import MarketRegimeDetector, market_regime_to_number, \
    number_to_market_regime
from zpython.util.model_market_regime import ModelMarketRegime, ModelMarketRegimeDetector


def max_price_diff(x):
    x = x.values
    cumsum = np.cumsum(x)
    max_cumsum = np.max(cumsum)
    price_diff = np.exp(max_cumsum) - 1
    return price_diff


def min_price_diff(x):
    x = x.values
    cumsum = np.cumsum(x)
    max_cumsum = np.min(cumsum)
    price_diff = np.exp(max_cumsum) - 1
    return price_diff


def _build_output(df: pd.DataFrame) -> np.ndarray:
    close = df["logReturn_closeBid_1min"]
    min_price = min_price_diff(close)
    max_price = max_price_diff(close)

    if min_price >= -0.0011 and max_price <= 0.0011:
        return np.array([0, 0, 1])
    if abs(min_price) > max_price:
        return np.array([0, 1, 0])
    return np.array([1, 0, 0])


def get_model_data_for_regime(
        data_read_function,
        regime: ModelMarketRegime,
        input_length: int,
        regime_detector,
        model_regime_detector
) -> tuple[list[pd.DataFrame], list[np.ndarray], pd.DataFrame, MarketRegimeDetector, ModelMarketRegimeDetector]:
    # Daten und Indikatoren laden
    data, regime_detector = create_indicators(data_read_function, regime_detector=regime_detector)

    # Regime zu numerischen Werten konvertieren
    data["regime"] = data["regime"].apply(number_to_market_regime)
    regimes_non_number = data["regime"]
    data["regime"] = regimes = regimes_non_number.apply(market_regime_to_number)

    # Dauer jedes Regime-Zustands berechnen
    regime_groups = (regimes != regimes.shift()).cumsum()
    regime_durations = regimes.groupby(regime_groups).cumcount() + 1

    # Regime-Schätzer vorbereiten
    if not model_regime_detector.is_fitted():
        model_regime_detector.fit(regime_durations, regimes)

    # Zeitverschiebungen berechnen
    input_shift = pd.Timedelta(minutes=input_length - 1)
    output_shift = pd.Timedelta(minutes=240)

    # Gültige Indizes bestimmen (nur die, bei denen ein vollständiges Fenster möglich ist)
    valid_idx = data.index[
        (data.index >= data.index[0] + input_shift) &
        (data.index <= data.index[-1] - output_shift)
        ]

    regimes_non_number = regimes_non_number[~regimes_non_number.index.duplicated(keep='first')]
    regime_durations = regime_durations[~regime_durations.index.duplicated(keep='first')]
    results = {}
    for index in valid_idx.values:
        results[index] = model_regime_detector.transform(regimes_non_number.loc[index], regime_durations.loc[index])

    model_market_regimes = pd.Series(results)
    valid_idx = model_market_regimes[model_market_regimes == regime].index
    one_min = pd.Timedelta(minutes=1)

    # Funktion zur Verarbeitung eines einzelnen Index
    def process_idx(idx):
        start = idx - input_shift
        end = idx + output_shift
        in_window = data.loc[start:idx]
        out_window = data.loc[idx + one_min:end]

        if in_window.isnull().values.any() or out_window.isnull().values.any() or len(in_window) != input_length or len(
                out_window) != 240:
            return None, None

        out = _build_output(out_window)
        return in_window, out

    # Parallelisierte Verarbeitung
    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(process_idx, valid_idx), total=len(valid_idx), desc="Slicing data in regimes"))

    # Nur gültige Fenster zurückgeben
    slices = [r for r in results if r[0] is not None]
    ins = [r[0] for r in slices]
    outs = [r[1] for r in slices]

    return ins, outs, data, regime_detector, model_regime_detector
