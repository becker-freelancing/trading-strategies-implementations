package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.Indicator;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.TRIndicator;
import org.ta4j.core.indicators.helpers.TransformIndicator;
import org.ta4j.core.num.DecimalNum;
import org.ta4j.core.num.Num;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;

public class VoltyExpanCloseStrategy extends BaseStrategy {

    private Indicator<Num> atrs;
    private BarSeries barSeries;
    private Direction direction;

    public VoltyExpanCloseStrategy() {
        super("voltan_expan_close_strategy", new PermutableStrategyParameter(
                new StrategyParameter("length", 5, 2, 10, 1),
                new StrategyParameter("num_atrs", 0.75, 0.5, 1., 0.1)
        ));
    }

    public VoltyExpanCloseStrategy(Map<String, Decimal> parameters) {
        super(parameters);

        int length = parameters.get("length").intValue();
        Num numAtrs = DecimalNum.valueOf(parameters.get("num_atrs").doubleValue());
        barSeries = new BaseBarSeries();

        TRIndicator trIndicator = new TRIndicator(barSeries);
        SMAIndicator smaIndicator = new SMAIndicator(trIndicator, length);
        atrs = new TransformIndicator(smaIndicator, value -> value.multipliedBy(numAtrs));
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {

        if (direction != null) {
            return Optional.of(entrySignalFactory.fromAmount(new Decimal(1), direction, Decimal.DOUBLE_MAX, Decimal.DOUBLE_MAX, PositionType.HARD_LIMIT, timeSeries.getEntryForTime(time)));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {

        updateData(timeSeries, time);

        if (direction != null) {
            return Optional.of(new ExitSignal(direction.negate()));
        }

        return Optional.empty();
    }

    private void updateData(TimeSeries timeSeries, LocalDateTime time) {
        Bar currentPrice = timeSeries.getEntryForTimeAsBar(time);
        TimeSeriesEntry lastPrice = timeSeries.getLastEntryForTime(time);
        barSeries.addBar(currentPrice);
        int endIndex = barSeries.getBarCount() - 1;

        Num atr = atrs.getValue(endIndex - 1);
        Decimal upper = lastPrice.getCloseMid().add(atr.doubleValue());
        Decimal lower = lastPrice.getCloseMid().subtract(atr.doubleValue());

        double currentClose = currentPrice.getClosePrice().doubleValue();

        if (upper.isLessThan(currentClose)) {
            direction = Direction.BUY;
        } else if (lower.isGreaterThan(currentClose)) {
            direction = Direction.SELL;
        } else {
            direction = null;
        }
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new VoltyExpanCloseStrategy(parameters);
    }
}
