package com.becker.freelance.strategies.regression.ai;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;

import java.util.Map;

public class TransformerModelStrategy extends AbstractRegressionModelStrategy {

    public TransformerModelStrategy() {
        super("transformer_model");
    }

    protected TransformerModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
    }

    @Override
    protected String getModelName() {
        return "transformer_model";
    }

    @Override
    protected int getModelId() {
        return 27;
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new TransformerModelStrategy(parameters);
    }
}
