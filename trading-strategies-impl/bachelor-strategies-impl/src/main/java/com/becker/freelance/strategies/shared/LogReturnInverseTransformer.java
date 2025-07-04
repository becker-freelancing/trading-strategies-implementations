package com.becker.freelance.strategies.shared;

import com.becker.freelance.commons.timeseries.TimeSeriesEntry;

import java.util.function.Function;

public interface LogReturnInverseTransformer<T> extends Function<TimeSeriesEntry, T> {

    public T transformLogReturnsToPrice(TimeSeriesEntry initialPrice);

    @Override
    default T apply(TimeSeriesEntry initialPrice) {
        return transformLogReturnsToPrice(initialPrice);
    }
}
