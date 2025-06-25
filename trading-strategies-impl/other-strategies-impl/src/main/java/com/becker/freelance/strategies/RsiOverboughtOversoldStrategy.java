package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import org.ta4j.core.indicators.RSIIndicator;

import java.util.Optional;

public class RsiOverboughtOversoldStrategy extends BaseStrategy {


    private final RSIIndicator rsiIndicator;
    private final Decimal limitDistance;
    private final Decimal stopDistance;


    public RsiOverboughtOversoldStrategy(StrategyParameter parameter, int rsiPeriod, Decimal limit, Decimal stop) {
        super(parameter);
        barSeries.setMaximumBarCount(rsiPeriod + 1);
        rsiIndicator = new RSIIndicator(closePrice, rsiPeriod);
        this.limitDistance = limit;
        this.stopDistance = stop;
    }


    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        int barCount = barSeries.getEndIndex();
        double value = rsiIndicator.getValue(barCount).doubleValue();

        TimeSeriesEntry currentEntry = entryParameter.currentPrice();
        TimeSeriesEntry lastEntry = entryParameter.timeSeries().getLastEntryForTime(entryParameter.time());

        if (value > 70 /*&& isBearishEngulfing(currentEntry, lastEntry)*/) {

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(Direction.SELL).asMarketOrder().withPair(entryParameter.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitDistanceToLevel(entryParameter.currentPrice(), limitDistance, Direction.SELL)))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopDistanceToLevel(entryParameter.currentPrice(), stopDistance, Direction.SELL))));
        } else if (value < 30 /*&& isBullishEngulfing(currentEntry, lastEntry)*/) {

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(entryParameter.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitDistanceToLevel(entryParameter.currentPrice(), limitDistance, Direction.BUY)))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopDistanceToLevel(entryParameter.currentPrice(), stopDistance, Direction.BUY))));
        }

        return Optional.empty();
    }

    private boolean isBullishEngulfing(TimeSeriesEntry currentEntry, TimeSeriesEntry lastEntry) {
        return true;
        //return currentEntry.isGreenCandle() && !lastEntry.isGreenCandle() && lastEntry.getHighMid().isLessThan(currentEntry.getCloseMid()) && lastEntry.getLowMid().isGreaterThan(currentEntry.getOpenMid());
    }

    private boolean isBearishEngulfing(TimeSeriesEntry currentEntry, TimeSeriesEntry lastEntry) {
        return true;
        //return !currentEntry.isGreenCandle() && lastEntry.isGreenCandle() && lastEntry.getHighMid().isLessThan(currentEntry.getOpenMid()) && lastEntry.getLowMid().isGreaterThan(currentEntry.getCloseMid());
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }
}
