import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from tqdm import tqdm

from zpython.util.model_data_creator import ModelMarketRegime


class MarketRegimePCA:

    def __init__(self, n_components):
        self.pcas = {key: PCA(n_components) for key in list(ModelMarketRegime)}

    def fit(self, scaled_data: dict[ModelMarketRegime, list[pd.DataFrame]]):

        for regime in tqdm(self.pcas.keys(), "Fitting PCA"):
            data_by_regime = scaled_data[regime]
            data_by_regime = pd.concat(data_by_regime)
            data_by_regime = data_by_regime[~data_by_regime.index.duplicated(keep='first')]
            self.pcas[regime].fit(data_by_regime)

    def transform(self, data: dict[ModelMarketRegime, list[pd.DataFrame]]) -> dict[ModelMarketRegime, list[np.ndarray]]:
        transformed_data = {}
        for regime in tqdm(data.keys(), "Transforming Data with PCA"):
            pca = self.pcas[regime]
            transformed = [pca.transform(X) for X in data[regime]]
            transformed_data[regime] = transformed
        return transformed_data

    def fit_transform(self, data: dict[ModelMarketRegime, list[pd.DataFrame]]) -> dict[
        ModelMarketRegime, list[np.ndarray]]:
        self.fit(data)
        return self.transform(data)
