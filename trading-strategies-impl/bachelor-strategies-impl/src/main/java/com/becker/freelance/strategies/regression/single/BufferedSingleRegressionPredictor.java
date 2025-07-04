package com.becker.freelance.strategies.regression.single;

import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.shared.PredictionParameter;

import java.util.Optional;

public class BufferedSingleRegressionPredictor implements SingleRegressionPredictor {

    @Override
    public Optional<SingleRegressionPrediction> predict(EntryExecutionParameter entryParameter, PredictionParameter predictionParameter) {
        return Optional.ofNullable(BufferedRegressionPredictionReader.getPredictionsSingleton()
                .get(entryParameter.time()));
    }
}
