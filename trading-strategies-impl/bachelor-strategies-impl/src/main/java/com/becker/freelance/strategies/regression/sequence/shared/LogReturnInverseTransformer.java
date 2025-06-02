package com.becker.freelance.strategies.regression.sequence.shared;

import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;

import java.util.function.Function;

public interface LogReturnInverseTransformer extends Function<TimeSeriesEntry, Decimal[]> {

    public Decimal[] transformLogReturnsToPrice(TimeSeriesEntry initialPrice);

    @Override
    default Decimal[] apply(TimeSeriesEntry initialPrice) {
        return transformLogReturnsToPrice(initialPrice);
    }
}
