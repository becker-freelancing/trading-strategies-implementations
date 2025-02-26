package com.becker.freelance.strategies.regression.ml;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;

import java.util.Map;

public class RidgeStrategy extends MlBaseStrategy {

    public RidgeStrategy() {
        super("ridge");
    }

    public RidgeStrategy(Map<String, Decimal> parameters) {
        super("ridge", "train_525_pred180", parameters);
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new RidgeStrategy(parameters);
    }
}
