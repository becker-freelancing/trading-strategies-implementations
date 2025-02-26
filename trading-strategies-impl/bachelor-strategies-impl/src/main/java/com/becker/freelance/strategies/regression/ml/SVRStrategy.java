package com.becker.freelance.strategies.regression.ml;

import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;
import com.becker.freelance.strategies.regression.shared.BufferedPredictor;
import com.becker.freelance.strategies.regression.shared.PredictionToEntrySignalConverter;

import java.util.Map;

public class SVRStrategy extends MlBaseStrategy {

    private BufferedPredictor predictor;
    private PredictionToEntrySignalConverter predictionToEntrySignalConverter;

    public SVRStrategy() {
        super("svr_strategy");
    }
    public SVRStrategy(Map<String, Decimal> parameters) {
        super("svr", "train_85_pred180", parameters);
    }

    private static boolean stopLossLessThanTakeProfitFilter(Map<String, Decimal> parameters) {
        return parameters.get("stop_in_euro").isLessThanOrEqualTo(parameters.get("limit_in_euro"));
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new SVRStrategy(parameters);
    }
}
