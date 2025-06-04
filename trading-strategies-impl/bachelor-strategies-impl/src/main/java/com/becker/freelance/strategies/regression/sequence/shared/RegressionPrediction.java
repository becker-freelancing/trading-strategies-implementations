package com.becker.freelance.strategies.regression.sequence.shared;

import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;

import java.time.LocalDateTime;

public record RegressionPrediction(LocalDateTime closeTime,
                                   TradeableQuantilMarketRegime regime,
                                   Double[] logReturns,
                                   Double[] cumulativeLogReturns,
                                   LogReturnInverseTransformer inverseTransformer) implements LogReturnInverseTransformer {
    @Override
    public Double[] transformLogReturnsToPrice(TimeSeriesEntry initialPrice) {
        return inverseTransformer().transformLogReturnsToPrice(initialPrice);
    }
}
