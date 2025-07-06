package com.becker.freelance.strategies.rl.read;

import com.becker.freelance.strategies.executionparameter.StrategyExecutionParameter;
import com.becker.freelance.strategies.shared.PredictionParameter;

import java.util.Optional;

public class BufferedRLOnlyLongPredictor implements RLPredictor {
    @Override
    public Optional<RLPrediction> predict(StrategyExecutionParameter parameter, PredictionParameter predictionParameter) {
        return Optional.ofNullable(BufferedRLPredictionReader.getPredictionsSingleton("prediction-bybit/RL_ONLY_LONG.csv").get(parameter.time()));
    }
}
