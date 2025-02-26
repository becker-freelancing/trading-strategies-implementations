package com.becker.freelance.strategies.regression.ai;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;

import java.util.Map;

public class CnnHalfYearModelStrategy extends AbstractRegressionModelStrategy {

    public CnnHalfYearModelStrategy() {
        super("cnn_half_year");
    }

    protected CnnHalfYearModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
    }

    @Override
    protected String getModelName() {
        return "cnn_half_year";
    }

    @Override
    protected int getModelId() {
        return 14;
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new CnnHalfYearModelStrategy(parameters);
    }
}
