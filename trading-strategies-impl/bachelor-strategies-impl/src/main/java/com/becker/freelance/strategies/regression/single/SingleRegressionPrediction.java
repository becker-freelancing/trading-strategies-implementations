package com.becker.freelance.strategies.regression.single;

import com.becker.freelance.commons.regime.TradeableMarketRegime;
import com.becker.freelance.strategies.shared.LogReturnInverseTransformer;

import java.time.LocalDateTime;

public record SingleRegressionPrediction(LocalDateTime closeTime,
                                         TradeableMarketRegime regime,
                                         Double min,
                                         Double max,
                                         LogReturnInverseTransformer<Double> minInverseTransformer,
                                         LogReturnInverseTransformer<Double> maxInverseTransformer) {

}
