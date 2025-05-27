import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

from zpython.util.model_data_creator import ModelMarketRegime


class MarketRegimeScaler:

    def __init__(self):
        self.scalers = {key: MinMaxScaler() for key in list(ModelMarketRegime)}

    def fit(self, data: dict[ModelMarketRegime, list[pd.DataFrame]]):

        for regime in tqdm(self.scalers.keys(), "Fitting scalers"):
            data_by_regime = data[regime]
            data_by_regime = pd.concat(data_by_regime)
            data_by_regime = data_by_regime[~data_by_regime.index.duplicated(keep='first')]
            self.scalers[regime].fit(data_by_regime)

    def transform(self, data: dict[ModelMarketRegime, list[pd.DataFrame]]) -> dict[
        ModelMarketRegime, list[pd.DataFrame]]:
        transformed = {}
        for regime in tqdm(data.keys(), "Transforming data"):
            data_by_regime = data[regime]
            scaler = self.scalers[regime]
            transformed[regime] = [pd.DataFrame(data=scaler.transform(df), columns=df.columns, index=df.index) for df in
                                   data_by_regime]

        return transformed

    def fit_transform(self, data: dict[ModelMarketRegime, list[pd.DataFrame]]) -> dict[
        ModelMarketRegime, list[pd.DataFrame]]:
        self.fit(data)
        return self.transform(data)
