package com.becker.freelance.strategies.regression.sequence.shared;

import com.becker.freelance.strategies.executionparameter.EntryParameter;

import java.util.Optional;

public class BufferedRegressionPredictor implements RegressionPredictor {

    @Override
    public Optional<RegressionPrediction> predict(EntryParameter entryParameter) {
        return Optional.ofNullable(BufferedRegressionPredictionReader.getPredictionsSingleton()
                .get(entryParameter.time()));
    }
}
