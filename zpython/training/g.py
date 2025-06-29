import shutil

from zpython.util.model_market_regime import ModelMarketRegime

b2 = "C:/Users/jasb/AppData/Roaming/krypto-java/data-bybit/"
base = "%s0_ETHUSDT_1_TRAIN_CLASSIFICATION_240_UP_HIGH_VOLA_033.pt" % b2

for regime in list(ModelMarketRegime):
    p = f"{b2}0_ETHUSDT_1_TRAIN_CLASSIFICATION_240_{regime.name}.pt"
    if base != p:
        shutil.copy(base, p)

    p = f"{b2}0_ETHUSDT_1_VAL_CLASSIFICATION_240_{regime.name}.pt"
    shutil.copy(base, p)
