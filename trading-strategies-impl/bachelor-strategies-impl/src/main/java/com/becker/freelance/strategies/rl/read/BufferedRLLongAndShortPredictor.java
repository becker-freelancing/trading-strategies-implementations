package com.becker.freelance.strategies.rl.read;

import com.becker.freelance.strategies.executionparameter.StrategyExecutionParameter;
import com.becker.freelance.strategies.shared.PredictionParameter;

import java.util.Optional;

public class BufferedRLLongAndShortPredictor implements RLPredictor {
    @Override
    public Optional<RLPrediction> predict(StrategyExecutionParameter parameter, PredictionParameter predictionParameter) {
        return Optional.ofNullable(BufferedRLPredictionReader.getPredictionsSingleton("prediction-bybit/RL_LONG_AND_SHORT.csv").get(parameter.time()));
    }
}
