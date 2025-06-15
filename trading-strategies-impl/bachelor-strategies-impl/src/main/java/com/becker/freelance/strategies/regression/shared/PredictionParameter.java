package com.becker.freelance.strategies.regression.shared;

import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;

import java.util.List;
import java.util.Map;

public interface PredictionParameter {

    public int regimeId();

    public Map<String, List<Double>> data();

    TradeableQuantilMarketRegime regime();
}
