package com.becker.freelance.strategies.regression.ml;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;
import com.becker.freelance.strategies.regression.shared.BufferedPredictor;
import com.becker.freelance.strategies.regression.shared.PredictionToEntrySignalConverter;

import java.util.Map;

public class SGDStrategy extends MlBaseStrategy {

    private BufferedPredictor predictor;
    private PredictionToEntrySignalConverter predictionToEntrySignalConverter;

    public SGDStrategy() {
        super("sgd");
    }
    public SGDStrategy(Map<String, Decimal> parameters) {
        super("sgd", "train_345_pred180", parameters);
    }

    private static boolean stopLossLessThanTakeProfitFilter(Map<String, Decimal> parameters) {
        return parameters.get("stop_in_euro").isLessThanOrEqualTo(parameters.get("limit_in_euro"));
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new SGDStrategy(parameters);
    }
}
