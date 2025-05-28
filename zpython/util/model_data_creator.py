from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from tqdm import tqdm

from zpython.util.indicator_creator import create_indicators
from zpython.util.market_regime import MarketRegimeDetector, market_regime_to_number, \
    number_to_market_regime
from zpython.util.model_market_regime import ModelMarketRegime, ModelMarketRegimeDetector


def get_regime(x, estimator):
    return None

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
    data["regime"] = data["regime"].apply(number_to_market_regime)
    regimes_non_number = data["regime"]
    data["regime"] = regimes = regimes_non_number.apply(market_regime_to_number)

    # Dauer jedes Regime-Zustands berechnen
    regime_groups = (regimes != regimes.shift()).cumsum()
    regime_durations = regimes.groupby(regime_groups).cumcount() + 1

    # Regime-Schätzer vorbereiten
    regime_estimator = ModelMarketRegimeDetector()
    regime_estimator.fit(regime_durations, regimes)

    # Zeitverschiebungen berechnen
    input_shift = pd.Timedelta(minutes=input_length - 1)
    output_shift = pd.Timedelta(minutes=output_length)
    window_length = input_length + output_length

    # Gültige Indizes bestimmen (nur die, bei denen ein vollständiges Fenster möglich ist)
    valid_idx = data.index[
        (data.index >= data.index[0] + input_shift) &
        (data.index <= data.index[-1] - output_shift)
        ]

    regimes_non_number = regimes_non_number[~regimes_non_number.index.duplicated(keep='first')]
    regime_durations = regime_durations[~regime_durations.index.duplicated(keep='first')]
    results = {}
    for index in valid_idx.values:
        results[index] = regime_estimator.transform(regimes_non_number.loc[index], regime_durations.loc[index])

    model_market_regimes = pd.Series(results)
    valid_idx = model_market_regimes[model_market_regimes == regime].index
    # Funktion zur Verarbeitung eines einzelnen Index
    def process_idx(idx):
        start = idx - input_shift
        end = idx + output_shift
        window = data.loc[start:end]

        if window.isnull().values.any() or len(window) != window_length:
            return None

        return window

    # Parallelisierte Verarbeitung
    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(process_idx, valid_idx), total=len(valid_idx), desc="Slicing data in regimes"))

    # Nur gültige Fenster zurückgeben
    slices = [r for r in results if r is not None]

    return slices, data, regime_detector
