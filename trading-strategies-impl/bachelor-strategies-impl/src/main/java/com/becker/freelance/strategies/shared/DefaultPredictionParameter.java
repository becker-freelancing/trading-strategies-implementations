package com.becker.freelance.strategies.shared;

import com.becker.freelance.commons.regime.TradeableMarketRegime;

import java.util.List;
import java.util.Map;

public record DefaultPredictionParameter(TradeableMarketRegime regime,
                                         Map<String, List<Double>> data) implements PredictionParameter {
    @Override
    public int regimeId() {
        return regime().id();
    }
}
