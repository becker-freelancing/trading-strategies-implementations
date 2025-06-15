package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.regression.shared.PredictionParameter;

import java.util.Optional;

public class BufferedRegressionPredictor implements RegressionPredictor {

    @Override
    public Optional<RegressionPrediction> predict(EntryExecutionParameter entryParameter, PredictionParameter predictionParameter) {
        return Optional.ofNullable(BufferedRegressionPredictionReader.getPredictionsSingleton()
                .get(entryParameter.time()));
    }
}
