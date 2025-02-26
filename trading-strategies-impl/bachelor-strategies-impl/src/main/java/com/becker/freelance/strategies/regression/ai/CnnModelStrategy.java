package com.becker.freelance.strategies.regression.ai;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;

import java.util.Map;

public class CnnModelStrategy extends AbstractRegressionModelStrategy {

    public CnnModelStrategy() {
        super("cnn");
    }

    protected CnnModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
    }

    @Override
    protected String getModelName() {
        return "cnn";
    }

    @Override
    protected int getModelId() {
        return 26;
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new CnnModelStrategy(parameters);
    }
}
