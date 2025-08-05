from zpython.model.best_model_loader import _get_metrics_by_regime
from zpython.util.model_market_regime import ModelMarketRegime

metrics_by_regime = _get_metrics_by_regime("models-bybit/SEQUENCE_REGRESSION")

for regime in list(ModelMarketRegime):
    metrics = metrics_by_regime[regime]
    metrics = metrics[~metrics["study"].str.contains("multiscale", case=False, na=False)]
    best = metrics.loc[metrics["val_loss"].idxmin()]
    print(f"\\textbfamp;{regime.name}amp2; & {best['study']} & {round(best['val_loss'], 2)} & {best['val_profit_hit_ratio']} & {best['val_loss_hit_ratio']} \\\\")