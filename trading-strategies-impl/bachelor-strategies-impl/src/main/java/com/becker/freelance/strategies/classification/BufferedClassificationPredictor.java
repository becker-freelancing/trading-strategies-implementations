package com.becker.freelance.strategies.classification;

import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.shared.PredictionParameter;

import java.util.Optional;

public class BufferedClassificationPredictor implements ClassificationPredictor {

    @Override
    public Optional<ClassificationPrediction> predict(EntryExecutionParameter entryParameter, PredictionParameter predictionParameter) {
        return Optional.ofNullable(BufferedClassificationPredictionReader.getPredictionsSingleton()
                .get(entryParameter.time()));
    }
}
