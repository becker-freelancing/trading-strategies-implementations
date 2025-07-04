package com.becker.freelance.strategies.classification;

import java.time.LocalDateTime;

public record ClassificationPrediction(LocalDateTime closeTime,
                                       Double buyProbability,
                                       Double sellProbability,
                                       Double noneProbability) {

    public Double maxProbabilityForBuyAndSell() {
        return Math.max(buyProbability(), sellProbability());
    }
}
