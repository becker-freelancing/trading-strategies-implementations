package com.becker.freelance.strategies.regression.ai;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;

import java.util.Map;

public class CnnHalfYearM5ModelStrategy extends AbstractRegressionModelStrategy {

    public CnnHalfYearM5ModelStrategy() {
        super("cnn_half_year_m5");
    }

    protected CnnHalfYearM5ModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
    }

    @Override
    protected String getModelName() {
        return "cnn_half_year_m5";
    }

    @Override
    protected int getModelId() {
        return 26;
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new CnnHalfYearM5ModelStrategy(parameters);
    }
}
