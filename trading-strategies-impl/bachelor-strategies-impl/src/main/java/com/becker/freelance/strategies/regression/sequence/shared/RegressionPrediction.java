package com.becker.freelance.strategies.regression.sequence.shared;

import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;

import java.time.LocalDateTime;

public record RegressionPrediction(LocalDateTime closeTime,
                                   TradeableQuantilMarketRegime regime,
                                   Decimal[] logReturns,
                                   Decimal[] cumulativeLogReturns,
                                   LogReturnInverseTransformer inverseTransformer) implements LogReturnInverseTransformer {
    @Override
    public Decimal[] transformLogReturnsToPrice(TimeSeriesEntry initialPrice) {
        return inverseTransformer().transformLogReturnsToPrice(initialPrice);
    }
}
