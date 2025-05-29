from enum import Enum

import numpy as np
import pandas as pd

from zpython.util.market_regime import MarketRegime


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


class ModelMarketRegimeDetector:

    def __init__(self, quantil_values=[0.33, 0.66, 1]):
        self.quantiles = {key: np.array([]) for key in list(MarketRegime)}
        self.quantil_values = quantil_values

    def fit(self, regime_durations: pd.Series, regimes: pd.Series):
        for r in self.quantiles.keys():
            self.quantiles[r] = np.array([
                np.quantile(regime_durations[regimes == r.value].values, q) for q in self.quantil_values
            ])

    def transform(self, last_regime: MarketRegime, regime_duration) -> ModelMarketRegime:
        q = self.quantiles[last_regime]
        idxs = np.argwhere(q > regime_duration)
        if len(idxs) == 0:
            return model_market_regime(last_regime, 1)

        return model_market_regime(last_regime, self.quantil_values[idxs[0][0]])

    def is_fitted(self):
        for q in self.quantiles.values():
            if len(q) == 0:
                return False
        return True
