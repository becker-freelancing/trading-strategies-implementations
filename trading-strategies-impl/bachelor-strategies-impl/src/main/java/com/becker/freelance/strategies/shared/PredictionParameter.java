package com.becker.freelance.strategies.shared;

import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;

import java.util.List;
import java.util.Map;

public interface PredictionParameter {

    public int regimeId();

    public Map<String, List<Double>> data();

    TradeableQuantilMarketRegime regime();
}
