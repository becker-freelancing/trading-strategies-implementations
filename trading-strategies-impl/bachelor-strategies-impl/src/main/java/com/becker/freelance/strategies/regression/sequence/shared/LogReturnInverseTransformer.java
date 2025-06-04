package com.becker.freelance.strategies.regression.sequence.shared;

import com.becker.freelance.commons.timeseries.TimeSeriesEntry;

import java.util.function.Function;

public interface LogReturnInverseTransformer extends Function<TimeSeriesEntry, Double[]> {

    public Double[] transformLogReturnsToPrice(TimeSeriesEntry initialPrice);

    @Override
    default Double[] apply(TimeSeriesEntry initialPrice) {
        return transformLogReturnsToPrice(initialPrice);
    }
}
