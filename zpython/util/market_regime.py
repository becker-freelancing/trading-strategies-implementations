
import numpy as np
import pandas as pd
import pandas_ta as ta

from zpython.util import split_on_gaps


def market_state_colors():
    return {
        MarketRegime.DOWN_HIGH_VOLA: "red",
        MarketRegime.DOWN_LOW_VOLA: "#FFCCCC",
        MarketRegime.SIDE_HIGH_VOLA: "blue",
        MarketRegime.SIDE_LOW_VOLA: "lightblue",
        MarketRegime.UP_HIGH_VOLA: "green",
        MarketRegime.UP_LOW_VOLA: "lightgreen"
    }


from enum import Enum


class MarketRegime(Enum):
    DOWN_HIGH_VOLA = 1
    DOWN_LOW_VOLA = 2
    SIDE_HIGH_VOLA = 3
    SIDE_LOW_VOLA = 4
    UP_HIGH_VOLA = 5
    UP_LOW_VOLA = 6


def number_to_market_regime(regime: MarketRegime | int):
    return MarketRegime(regime) if isinstance(regime, int) else regime


def market_regime_to_number(regime: MarketRegime | int):
    return regime.value if isinstance(regime, MarketRegime) else regime


def market_regime_to_number_if_needed(df: pd.DataFrame, regime_column="regime"):
    if isinstance(df[regime_column].iloc[0], MarketRegime):
        df[regime_column] = df[regime_column].apply(market_regime_to_number)
    return df


def split_on_regimes(df: pd.DataFrame, regime_column="regime") -> dict[MarketRegime, pd.DataFrame]:
    result = {}
    if isinstance(df[regime_column].iloc[0], MarketRegime):
        for regime in list(MarketRegime):
            result[regime] = df[df[regime_column] == regime]
    else:
        for regime in list(MarketRegime):
            result[regime] = df[df[regime_column] == regime.value]

    return result



class MarketRegimeDetector:

    def __init__(self, trend_reversal_slope_threshold=0.05, trend_slope_shift=15):
        self.trend_reversal_slope_threshold = trend_reversal_slope_threshold
        self.vola_split_threshold = None
        self.trend_slope_shift = trend_slope_shift

    def is_fitted(self):
        return self.vola_split_threshold is not None

    def fit_transform(self, df, close_column="closeBid", time_frame=1):
        self.fit(df, close_column, time_frame)
        return self.transform(df, close_column, time_frame)

    def fit(self, df, close_column="closeBid", time_frame=1):
        dfs = split_on_gaps(df, time_frame)
        returns = [np.log(data[close_column] / data[close_column].shift(1)) for data in dfs]
        volas = [data.rolling(window=30).std() for data in returns]
        vola_split_thresholds = [vola.quantile(0.5) for vola in volas]
        self.vola_split_threshold = np.mean(vola_split_thresholds)

    def transform(self, df, close_column="closeBid", time_frame=1) -> pd.Series:
        if not self.vola_split_threshold:
            raise Exception("Market Regime Detector must be fitted first")

        dfs = split_on_gaps(df, time_frame)
        # Calculate Trends
        trends = []
        for data in dfs:
            close = data[close_column]
            ema_50 = ta.ema(close, 50)
            ema_100 = ta.ema(close, 100)
            ema_50_slope = (ema_50 - ema_50.shift(self.trend_slope_shift)) / self.trend_slope_shift

            trend = pd.Series(0, index=data.index)
            up = (ema_50 > ema_100) & (ema_50_slope > -self.trend_reversal_slope_threshold)
            down = (ema_50 < ema_100) & (ema_50_slope < self.trend_reversal_slope_threshold)
            trend.loc[up[up == True].index] = 1
            trend.loc[down[down == True].index] = -1
            trends.append(trend)

        # Calculate Volas
        volas = []
        for data in dfs:
            close = data[close_column]
            returns = np.log(close / close.shift(1))
            vola = returns.rolling(window=30).std()

            low = vola <= self.vola_split_threshold
            vola = pd.Series(1, index=data.index)
            vola.loc[low[low == True].index] = -1
            volas.append(vola)

        # Detect Regimes
        regimes = []
        for trend, vola in zip(trends, volas):
            regime = pd.Series(MarketRegime.DOWN_HIGH_VOLA, index=trend.index)

            downLowVola = (trend == -1) & (vola == 1)
            regime.loc[downLowVola[downLowVola == True].index] = MarketRegime.DOWN_LOW_VOLA

            sideHighvola = (trend == 0) & (vola == 1)
            regime.loc[sideHighvola[sideHighvola == True].index] = MarketRegime.SIDE_HIGH_VOLA

            sideLowVola = (trend == 0) & (vola == -1)
            regime.loc[sideLowVola[sideLowVola == True].index] = MarketRegime.SIDE_LOW_VOLA

            upHighVola = (trend == 1) & (vola == 1)
            regime.loc[upHighVola[upHighVola == True].index] = MarketRegime.UP_HIGH_VOLA

            upLowVola = (trend == 1) & (vola == -1)
            regime.loc[upLowVola[upLowVola == True].index] = MarketRegime.UP_LOW_VOLA

            regimes.append(regime)

        return pd.concat(regimes)
