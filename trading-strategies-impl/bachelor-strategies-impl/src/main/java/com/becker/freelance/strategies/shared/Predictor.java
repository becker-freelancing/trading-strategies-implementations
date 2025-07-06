package com.becker.freelance.strategies.shared;

import com.becker.freelance.indicators.ta.regime.QuantileMarketRegime;
import com.becker.freelance.strategies.executionparameter.StrategyExecutionParameter;

import java.util.Optional;

public interface Predictor<T> {

    public Optional<T> predict(StrategyExecutionParameter parameter, PredictionParameter predictionParameter);

    public default boolean requiresPredictionParameter() {
        return false;
    }

    public default int requiredInputLengthForRegime(QuantileMarketRegime regime) {
        return 1;
    }

    public default int getMaxRequiredInputLength() {
        return 1;
    }
}
