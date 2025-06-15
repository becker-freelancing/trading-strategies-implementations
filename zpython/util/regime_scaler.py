import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

from zpython.util.model_data_creator import ModelMarketRegime


class MarketRegimeScaler:

    def __init__(self):
        self.scalers = {key: MinMaxScaler() for key in list(ModelMarketRegime)}

    def fit(self, data: list[pd.DataFrame], regime: ModelMarketRegime):
        data_by_regime = pd.concat(data)
        data_by_regime = data_by_regime[~data_by_regime.index.duplicated(keep='first')]
        self.scalers[regime].fit(data_by_regime)

    def transform(self, data: list[pd.DataFrame], regime: ModelMarketRegime) -> list[pd.DataFrame]:
        scaler = self.scalers[regime]
        transformed = [
            pd.DataFrame(data=scaler.transform(df[scaler.feature_names_in_]), columns=df.columns, index=df.index) for df
            in
                       tqdm(data, f"Transforming Data for regime {regime.name}")]

        return transformed

    def fit_transform(self, data: list[pd.DataFrame], regime: ModelMarketRegime) -> list[pd.DataFrame]:
        self.fit(data, regime)
        return self.transform(data, regime)

    def _reshape(self, data: list[pd.DataFrame], regime: ModelMarketRegime) -> list[pd.DataFrame]:
        scaler = self.scalers[regime]
        result = []
        for unshaped in data:
            reshaped = np.zeros((len(unshaped), len(scaler.feature_names_in_)))
            reshaped = pd.DataFrame(data=reshaped, columns=scaler.feature_names_in_, index=unshaped.index)
            reshaped[unshaped.columns] = unshaped[unshaped.columns]
            result.append(reshaped)
        return result

    def inverse_transform(self, data: list[pd.DataFrame], regime: ModelMarketRegime) -> list[pd.DataFrame]:
        scaler = self.scalers[regime]
        reshaped = self._reshape(data, regime)
        inverse = [pd.DataFrame(data=scaler.inverse_transform(df), columns=df.columns, index=df.index) for df in
                   tqdm(reshaped, f"Inverse transforming Data for regime {regime.name}")]
        inverse = [inv[df.columns] for inv, df in zip(inverse, data)]
        return inverse
