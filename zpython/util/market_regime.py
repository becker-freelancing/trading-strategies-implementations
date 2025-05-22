from enum import Enum

import numpy as np
import pandas as pd
import pandas_ta as ta

from zpython.indicators.indicator_creator import _split_on_gaps


def market_state_colors():
    return {
        MarketState.DOWN_HIGH_VOLA: "red",
        MarketState.DOWN_LOW_VOLA: "#FFCCCC",
        MarketState.SIDE_HIGH_VOLA: "blue",
        MarketState.SIDE_LOW_VOLA: "lightblue",
        MarketState.UP_HIGH_VOLA: "green",
        MarketState.UP_LOW_VOLA: "lightgreen"
    }


class MarketState(Enum):
    DOWN_HIGH_VOLA = 1,
    DOWN_LOW_VOLA = 2,
    SIDE_HIGH_VOLA = 3,
    SIDE_LOW_VOLA = 4,
    UP_HIGH_VOLA = 5,
    UP_LOW_VOLA = 6


class MarketRegimeDetector:

    def __init__(self, trend_reversal_slope_threshold=0.05, trend_slope_shift=15):
        self.trend_reversal_slope_threshold = trend_reversal_slope_threshold
        self.vola_split_threshold = None
        self.trend_slope_shift = trend_slope_shift

    def _calculate_metadata(self, df, close_column, time_frame, slope_shift):
        df = df.copy()
        df = df.reset_index(drop=True)
        dfs = _split_on_gaps(df, time_frame)
        for data in dfs:
            if "trend" in data.columns.values:
                continue
            data.set_index("closeTime", inplace=True)
            data["EMA_50"] = ta.ema(data[close_column], 50)
            data["EMA_100"] = ta.ema(data[close_column], 100)
            data["EMA_50_SLOPE"] = (data["EMA_50"] - data["EMA_50"].shift(slope_shift)) / slope_shift

            data["trend"] = 0
            up = (data["EMA_50"] > data["EMA_100"]) & (data["EMA_50_SLOPE"] > -self.trend_reversal_slope_threshold)
            down = (data["EMA_50"] < data["EMA_100"]) & (data["EMA_50_SLOPE"] < self.trend_reversal_slope_threshold)
            data.loc[up[up == True].index, "trend"] = 1
            data.loc[down[down == True].index, "trend"] = -1
            data.reset_index(inplace=True)

        for data in dfs:
            if "volatility_class" in data.columns.values:
                continue
            data["Return"] = np.log(data["closeBid"] / data["closeBid"].shift(1))
            data["volatility"] = data["Return"].rolling(window=30).std()

            high_thres = data["volatility"].quantile(0.5)

            high = data["volatility"] > high_thres
            low = data["volatility"] < high_thres
            df["volatility_class"] = 0
            df.loc[high[high == True].index, "volatility_class"] = 1
            df.loc[low[low == True].index, "volatility_class"] = -1

        return pd.concat(dfs)

    def fit_transform(self, df, close_column="closeBid", time_frame=1):
        self.fit(df, close_column, time_frame)
        return self.transform(df, close_column, time_frame)

    def fit(self, df, close_column="closeBid", time_frame=1):
        dfs = _split_on_gaps(df, time_frame)
        returns = [np.log(data[close_column] / data[close_column].shift(1)) for data in dfs]
        volas = [data.rolling(window=30).std() for data in returns]
        vola_split_thresholds = [vola.quantile(0.5) for vola in volas]
        self.vola_split_threshold = np.mean(vola_split_thresholds)

    def transform(self, df, close_column="closeBid", time_frame=1) -> pd.Series:
        if not self.vola_split_threshold:
            raise Exception("Market Regime Detector must be fitted first")

        dfs = _split_on_gaps(df, time_frame)
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
            regime = pd.Series(MarketState.DOWN_HIGH_VOLA, index=trend.index)

            downLowVola = (trend == -1) & (vola == 1)
            regime.loc[downLowVola[downLowVola == True].index] = MarketState.DOWN_LOW_VOLA

            sideHighvola = (trend == 0) & (vola == 1)
            regime.loc[sideHighvola[sideHighvola == True].index] = MarketState.SIDE_HIGH_VOLA

            sideLowVola = (trend == 0) & (vola == -1)
            regime.loc[sideLowVola[sideLowVola == True].index] = MarketState.SIDE_LOW_VOLA

            upHighVola = (trend == 1) & (vola == 1)
            regime.loc[upHighVola[upHighVola == True].index] = MarketState.UP_HIGH_VOLA

            upLowVola = (trend == 1) & (vola == -1)
            regime.loc[upLowVola[upLowVola == True].index] = MarketState.UP_LOW_VOLA

            regimes.append(regime)

        return pd.concat(regimes)
