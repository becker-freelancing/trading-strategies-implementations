package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.strategies.executionparameter.StrategyExecutionParameter;
import com.becker.freelance.strategies.shared.PredictionParameter;

import java.util.Optional;

public class BufferedRegressionPredictor implements RegressionPredictor {

    @Override
    public Optional<RegressionPrediction> predict(StrategyExecutionParameter entryParameter, PredictionParameter predictionParameter) {
        return Optional.ofNullable(BufferedRegressionPredictionReader.getPredictionsSingleton()
                .get(entryParameter.time()));
    }
}
