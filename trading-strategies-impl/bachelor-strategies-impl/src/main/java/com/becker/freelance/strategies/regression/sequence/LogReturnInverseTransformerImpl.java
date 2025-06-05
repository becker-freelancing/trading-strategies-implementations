package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.strategies.regression.shared.LogReturnInverseTransformer;


public class LogReturnInverseTransformerImpl implements LogReturnInverseTransformer<Double[]> {

    private final Double[] logReturns;

    public LogReturnInverseTransformerImpl(Double[] logReturns) {
        this.logReturns = logReturns;
    }

    @Override
    public Double[] transformLogReturnsToPrice(TimeSeriesEntry initialPrice) {
        if (logReturns.length == 0) {
            return new Double[0];
        }
        Double[] transformed = new Double[logReturns.length];
        transformed[0] = inverseTransform(logReturns[0], initialPrice.getCloseMid().doubleValue());
        for (int i = 1; i < logReturns.length; i++) {
            transformed[i] = inverseTransform(logReturns[i], transformed[i - 1]);
        }
        return transformed;
    }

    private Double inverseTransform(Double logReturn, Double priceBefore) {
        return Math.exp(logReturn) * priceBefore;
    }
}
