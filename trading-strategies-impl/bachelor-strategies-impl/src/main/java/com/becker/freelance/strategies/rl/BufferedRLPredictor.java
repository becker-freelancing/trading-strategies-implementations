package com.becker.freelance.strategies.rl;

import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.shared.PredictionParameter;

import java.util.Optional;

public class BufferedRLPredictor implements RLPredictor {
    @Override
    public Optional<RLPrediction> predict(EntryExecutionParameter parameter, PredictionParameter predictionParameter) {
        return Optional.ofNullable(BufferedRLPredictionReader.getPredictionsSingleton().get(parameter.time()));
    }
}
