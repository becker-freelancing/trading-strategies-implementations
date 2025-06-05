package com.becker.freelance.strategies.regression.single;

import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.strategies.regression.shared.LogReturnInverseTransformer;


public class LogReturnInverseTransformerImpl implements LogReturnInverseTransformer<Double> {

    private final Double logReturn;

    public LogReturnInverseTransformerImpl(Double logReturn) {
        this.logReturn = logReturn;
    }

    @Override
    public Double transformLogReturnsToPrice(TimeSeriesEntry initialPrice) {
        return inverseTransform(logReturn, initialPrice.getCloseMid().doubleValue());
    }

    private Double inverseTransform(Double logReturn, Double priceBefore) {
        return Math.exp(logReturn) * priceBefore;
    }
}
