package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.strategies.regression.shared.LogReturnInverseTransformer;

import java.time.LocalDateTime;
import java.util.Arrays;

public record RegressionPrediction(LocalDateTime closeTime,
                                   TradeableQuantilMarketRegime regime,
                                   Double[] logReturns,
                                   Double[] cumulativeLogReturns,
                                   LogReturnInverseTransformer<Double[]> inverseTransformer) implements LogReturnInverseTransformer<Double[]> {
    @Override
    public Double[] transformLogReturnsToPrice(TimeSeriesEntry initialPrice) {
        return inverseTransformer().transformLogReturnsToPrice(initialPrice);
    }

    @Override
    public String toString() {
        return "RegressionPrediction{" +
                "closeTime=" + closeTime +
                ", regime=" + regime +
                ", logReturns=" + Arrays.toString(logReturns) +
                ", cumulativeLogReturns=" + Arrays.toString(cumulativeLogReturns) +
                ", inverseTransformer=" + inverseTransformer +
                '}';
    }
}
