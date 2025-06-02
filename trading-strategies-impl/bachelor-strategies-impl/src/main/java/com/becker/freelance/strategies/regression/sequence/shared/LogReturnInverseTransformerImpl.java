package com.becker.freelance.strategies.regression.sequence.shared;

import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;


public class LogReturnInverseTransformerImpl implements LogReturnInverseTransformer {

    private final Decimal[] logReturns;

    public LogReturnInverseTransformerImpl(Decimal[] logReturns) {
        this.logReturns = logReturns;
    }

    @Override
    public Decimal[] transformLogReturnsToPrice(TimeSeriesEntry initialPrice) {
        if (logReturns.length == 0) {
            return new Decimal[0];
        }
        Decimal[] transformed = new Decimal[logReturns.length];
        transformed[0] = inverseTransform(logReturns[0], initialPrice.getCloseMid());
        for (int i = 1; i < logReturns.length; i++) {
            transformed[i] = inverseTransform(logReturns[i], transformed[i - 1]);
        }
        return transformed;
    }

    private Decimal inverseTransform(Decimal logReturn, Decimal priceBefore) {
        return Decimal.exp(logReturn).multiply(priceBefore);
    }
}
