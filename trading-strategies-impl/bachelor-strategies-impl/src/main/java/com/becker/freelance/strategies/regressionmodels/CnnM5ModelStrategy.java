package com.becker.freelance.strategies.regressionmodels;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;

import java.util.Map;

public class CnnM5ModelStrategy extends AbstractRegressionModelStrategy {

    public CnnM5ModelStrategy() {
        super("cnn_m5");
    }

    protected CnnM5ModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
    }

    @Override
    protected String getModelName() {
        return "cnn_m5";
    }

    @Override
    protected int getModelId() {
        return 14;
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new CnnM5ModelStrategy(parameters);
    }
}
