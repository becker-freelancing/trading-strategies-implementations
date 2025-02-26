package com.becker.freelance.strategies.regression.ai;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;

import java.util.Map;

public class CnnTwoYearModelStrategy extends AbstractRegressionModelStrategy {

    public CnnTwoYearModelStrategy() {
        super("cnn_two_year");
    }

    protected CnnTwoYearModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
    }

    @Override
    protected String getModelName() {
        return "cnn_two_year";
    }

    @Override
    protected int getModelId() {
        return 20;
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new CnnTwoYearModelStrategy(parameters);
    }
}
