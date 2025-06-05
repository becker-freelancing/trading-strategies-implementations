package com.becker.freelance.strategies.regression.single;

import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;
import com.becker.freelance.strategies.regression.shared.LogReturnInverseTransformer;

import java.time.LocalDateTime;

public record SingleRegressionPrediction(LocalDateTime closeTime,
                                         TradeableQuantilMarketRegime regime,
                                         Double min,
                                         Double max,
                                         LogReturnInverseTransformer<Double> minInverseTransformer,
                                         LogReturnInverseTransformer<Double> maxInverseTransformer) {

}
