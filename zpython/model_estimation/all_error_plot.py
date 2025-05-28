import os

import pandas as pd

from zpython.util.model_data_creator import ModelMarketRegime

BASE_PATH = "C:/Users/jasb/AppData/Roaming/krypto-java/models-bybit/SEQUENCE_REGRESSION"

all_metrics = None

for root, dirs, files in os.walk(BASE_PATH):
    path = root.split(os.sep)
    print((len(path) - 1) * '---', os.path.basename(root))
    for file in files:
        if "a-metrics" in file:
            read_path = root + "/" + file
            read = pd.read_csv(read_path)
            read["model_name"] = path[1]
            if all_metrics is not None:
                all_metrics = pd.concat([all_metrics, read], ignore_index=True)
            else:
                all_metrics = read

for regime in list(ModelMarketRegime):
    regime_data = all_metrics[all_metrics["regime_id"] == regime.value]
    min_idx = regime_data.nsmallest(3, 'val_loss').index
    min_values = regime_data.loc[min_idx]
    print(regime)
    for idx, row in min_values.iterrows():
        print(
            f"\t Model: {row['model_name']}, Epoch: {row['epoch']}, Trial: {row['trial']}, Val_Loss: {row['val_loss']}")
    print()
