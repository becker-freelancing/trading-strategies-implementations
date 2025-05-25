import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from tqdm import tqdm

from zpython.util.market_regime import MarketRegime


class MarketRegimePCA:

    def __init__(self, n_components):
        self.pcas = {key: PCA(n_components) for key in list(MarketRegime)}

    def fit(self, complete_data: pd.DataFrame, scaler, regime_column="regime"):

        complete_data = complete_data.dropna()
        for regime in list(MarketRegime):
            data_by_regime = complete_data[complete_data[regime_column] == regime.value]
            data_by_regime = scaler.transform(data_by_regime)
            self.pcas[regime] = self.pcas[regime].fit(data_by_regime)

    def transform(self, data: dict[MarketRegime, list[np.ndarray]]) -> dict[MarketRegime, list[np.ndarray]]:
        transformed_data = {}
        for regime in tqdm(data.keys(), "Transforming Data with PCA"):
            pca = self.pcas[regime]
            transformed = [pca.transform(X) for X in data[regime]]
            transformed_data[regime] = transformed
        return transformed_data
