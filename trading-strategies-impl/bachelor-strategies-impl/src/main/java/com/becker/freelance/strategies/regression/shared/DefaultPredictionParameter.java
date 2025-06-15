package com.becker.freelance.strategies.regression.shared;

import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;

import java.util.List;
import java.util.Map;

public record DefaultPredictionParameter(TradeableQuantilMarketRegime regime,
                                         Map<String, List<Double>> data) implements PredictionParameter {
    @Override
    public int regimeId() {
        return regime().id();
    }
}
