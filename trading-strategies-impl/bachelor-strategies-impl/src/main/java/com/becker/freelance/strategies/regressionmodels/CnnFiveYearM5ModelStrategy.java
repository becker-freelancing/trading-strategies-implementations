package com.becker.freelance.strategies.regressionmodels;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;

import java.util.Map;

public class CnnFiveYearM5ModelStrategy extends AbstractRegressionModelStrategy {

    public CnnFiveYearM5ModelStrategy() {
        super("cnn_five_year_m5");
    }

    protected CnnFiveYearM5ModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
    }

    @Override
    protected String getModelName() {
        return "cnn_five_year_m5";
    }

    @Override
    protected int getModelId() {
        return 27;
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new CnnFiveYearM5ModelStrategy(parameters);
    }
}
