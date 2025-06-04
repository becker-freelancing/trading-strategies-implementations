package com.becker.freelance.strategies.regression.sequence.shared;

import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;

import java.util.Optional;

public class BufferedRegressionPredictor implements RegressionPredictor {

    @Override
    public Optional<RegressionPrediction> predict(EntryExecutionParameter entryParameter) {
        return Optional.ofNullable(BufferedRegressionPredictionReader.getPredictionsSingleton()
                .get(entryParameter.time()));
    }
}
