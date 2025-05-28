import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from tqdm import tqdm

from zpython.util.model_data_creator import ModelMarketRegime


class MarketRegimePCA:

    def __init__(self, n_components):
        self.pcas = {key: PCA(n_components) for key in list(ModelMarketRegime)}

    def fit(self, scaled_data: list[pd.DataFrame], regime: ModelMarketRegime):
        data_by_regime = pd.concat(scaled_data)
        data_by_regime = data_by_regime[~data_by_regime.index.duplicated(keep='first')]
        self.pcas[regime].fit(data_by_regime)

    def transform(self, data: list[pd.DataFrame], regime: ModelMarketRegime) -> list[np.ndarray]:
        pca = self.pcas[regime]
        transformed = [pca.transform(X) for X in tqdm(data, f"Transforming data for regime {regime.name} with PCA")]
        return transformed

    def fit_transform(self, data: list[pd.DataFrame], regime: ModelMarketRegime) -> list[np.ndarray]:
        self.fit(data, regime)
        return self.transform(data, regime)
