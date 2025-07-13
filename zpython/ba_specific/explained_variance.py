import matplotlib

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import joblib
from zpython.util.path_util import from_relative_path
from zpython.util.model_market_regime import ModelMarketRegime, ModelMarketRegimeDetector, to_str
from zpython.util.market_regime import number_to_market_regime, market_regime_to_number
from zpython.util.data_split import train_data
from zpython.util.indicator_creator import create_indicators
from zpython.util.regime_pca import MarketRegimePCA
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

plt.rcParams.update({
    "font.size": 20,
    "axes.titlesize": 25,
    "axes.labelsize": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 18
})
scaler = joblib.load(from_relative_path("data-bybit/a-scaler_SEQUENCE_REGRESSION.dump"))


def read_train(time_frame):
    return train_data()


data = create_indicators(data_read_function=read_train)[0].iloc[-400000:]

# Regime zu numerischen Werten konvertieren
data["regime"] = data["regime"].apply(number_to_market_regime)
regimes_non_number = data["regime"]
data["regime"] = regimes = regimes_non_number.apply(market_regime_to_number)

# Dauer jedes Regime-Zustands berechnen
regime_groups = (regimes != regimes.shift()).cumsum()
regime_durations = regimes.groupby(regime_groups).cumcount() + 1

regime = ModelMarketRegimeDetector()
regime.fit(regime_durations, regimes)

input_shift = pd.Timedelta(minutes=100 - 1)
output_shift = pd.Timedelta(minutes=30)
window_length = 130

valid_idx = data.index[
    (data.index >= data.index[0] + input_shift) &
    (data.index <= data.index[-1] - output_shift)
    ]

results = {}
for index in valid_idx.values:
    try:
        results[index] = regime.transform(regimes_non_number.loc[index], regime_durations.loc[index])
    except Exception as e:
        print(e)

model_market_regimes = pd.Series(results)


def process_idx(idx):
    start = idx - input_shift
    end = idx + output_shift
    window = data.loc[start:end]

    if window.isnull().values.any() or len(window) != window_length:
        return None, None

    return model_market_regimes.loc[idx], window


# Parallelisierte Verarbeitung
with ThreadPoolExecutor() as executor:
    results = list(tqdm(executor.map(process_idx, valid_idx), total=len(valid_idx), desc="Slicing data in regimes"))

# Nur gültige Fenster zurückgeben
slices = [r for r in results if r[0] is not None]

by_regime = {reg: [] for reg in list(ModelMarketRegime)}

for reg, slice in slices:
    by_regime[reg].append(slice)

pcas = MarketRegimePCA(None)

for regime in list(ModelMarketRegime):
    data = by_regime[regime]
    data = scaler.transform(data, regime)
    pcas.fit(data, regime)

# Plot
for regime in list(ModelMarketRegime):
    explained_variance_ratio = pcas.pcas[regime].explained_variance_ratio_
    cumulative_variance = np.cumsum(explained_variance_ratio)
    plt.plot(range(1, len(cumulative_variance) + 1), cumulative_variance, label=f'Regime: {to_str(regime)}')

plt.xlabel('Principal Components')
plt.ylabel('Cumulative Explained Variance')
plt.title('Explained Variance Plot')
plt.legend(loc='best')
plt.grid(True)
plt.xticks(list(range(0, 11)) + [20, 30, 40, 50])
plt.show()
