package com.becker.freelance.strategies.classification;

import com.becker.freelance.strategies.executionparameter.StrategyExecutionParameter;
import com.becker.freelance.strategies.shared.PredictionParameter;

import java.util.Optional;

public class BufferedClassificationWithoutPcaPredictor implements ClassificationPredictor {

    @Override
    public Optional<ClassificationPrediction> predict(StrategyExecutionParameter entryParameter, PredictionParameter predictionParameter) {
        return Optional.ofNullable(BufferedClassificationPredictionReader.getPredictionsSingleton("prediction-bybit/BACKTEST_PREDICTION_CLASSIFICATION_240_WITHOUT_PCA.csv")
                .get(entryParameter.time()));
    }
}
