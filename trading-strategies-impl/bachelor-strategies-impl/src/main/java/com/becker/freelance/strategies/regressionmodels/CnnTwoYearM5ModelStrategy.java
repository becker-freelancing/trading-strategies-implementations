package com.becker.freelance.strategies.regressionmodels;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;

import java.util.Map;

public class CnnTwoYearM5ModelStrategy extends AbstractRegressionModelStrategy {

    public CnnTwoYearM5ModelStrategy() {
        super("cnn_two_year_m5");
    }

    protected CnnTwoYearM5ModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
    }

    @Override
    protected String getModelName() {
        return "cnn_two_year_m5";
    }

    @Override
    protected int getModelId() {
        return 25;
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new CnnTwoYearM5ModelStrategy(parameters);
    }
}
