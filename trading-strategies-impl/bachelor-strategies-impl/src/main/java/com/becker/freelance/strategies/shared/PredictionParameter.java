package com.becker.freelance.strategies.shared;

import com.becker.freelance.commons.regime.TradeableMarketRegime;

import java.util.List;
import java.util.Map;

public interface PredictionParameter {

    public int regimeId();

    public Map<String, List<Double>> data();

    TradeableMarketRegime regime();
}
