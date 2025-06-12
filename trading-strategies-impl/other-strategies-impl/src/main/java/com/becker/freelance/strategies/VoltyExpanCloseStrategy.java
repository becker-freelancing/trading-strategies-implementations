package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import org.ta4j.core.Indicator;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.TRIndicator;
import org.ta4j.core.indicators.helpers.TransformIndicator;
import org.ta4j.core.num.Num;

import java.time.LocalDateTime;
import java.util.Optional;

public class VoltyExpanCloseStrategy extends BaseStrategy {

    private Indicator<Num> atrs;
    private Direction direction;


    public VoltyExpanCloseStrategy(StrategyParameter parameter, int period, Num numAtrs) {
        super(parameter);
        TRIndicator trIndicator = new TRIndicator(barSeries);
        SMAIndicator smaIndicator = new SMAIndicator(trIndicator, period);
        atrs = new TransformIndicator(smaIndicator, value -> value.multipliedBy(numAtrs));
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        if (direction != null) {

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(direction).asMarketOrder().withPair(entryParameter.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(Decimal.DOUBLE_MAX))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(new Decimal(1))));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {

        updateData(exitParameter.timeSeries(), exitParameter.time());

        if (direction != null) {
            return Optional.of(new ExitSignal(direction.negate()));
        }

        return Optional.empty();
    }

    private void updateData(TimeSeries timeSeries, LocalDateTime time) {
        TimeSeriesEntry lastPrice = timeSeries.getLastEntryForTime(time);
        int endIndex = barSeries.getEndIndex();

        Num atr = atrs.getValue(endIndex - 1);
        Decimal upper = lastPrice.getCloseMid().add(atr.doubleValue());
        Decimal lower = lastPrice.getCloseMid().subtract(atr.doubleValue());

        double currentClose = timeSeries.getEntryForTimeAsBar(time).getClosePrice().doubleValue();

        if (upper.isLessThan(currentClose)) {
            direction = Direction.BUY;
        } else if (lower.isGreaterThan(currentClose)) {
            direction = Direction.SELL;
        } else {
            direction = null;
        }
    }
}
