package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.util.Optional;

public class MA3Strategy extends BaseStrategy {

    private final Decimal stopDistance;
    private final Decimal limitDistance;
    private final SMAIndicator shortSma;
    private final SMAIndicator midSma;
    private final SMAIndicator longSma;
    private final Decimal minSlope;
    private final int minSlopeWindow;

    public MA3Strategy(StrategyParameter parameter, int longMaPeriod, int shortMaPeriod, int midMaPeriod, Decimal minSlope, int minSlopeWindow, Decimal stop, Decimal limit) {
        super(parameter);
        this.minSlope = minSlope;
        this.minSlopeWindow = minSlopeWindow;
        this.stopDistance = stop;
        this.limitDistance = limit;
        barSeries.setMaximumBarCount(longMaPeriod + 5);
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        shortSma = new SMAIndicator(closePriceIndicator, shortMaPeriod);
        midSma = new SMAIndicator(closePriceIndicator, midMaPeriod);
        longSma = new SMAIndicator(closePriceIndicator, longMaPeriod);
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        Optional<Direction> trendDirection = getTrendDirection();
        if (trendDirection.isEmpty()) {
            return Optional.empty();
        }

        int barCount = barSeries.getEndIndex();
        double currentShortSma = shortSma.getValue(barCount).doubleValue();
        double lastShortSmaValue = shortSma.getValue(barCount - 1).doubleValue();
        double currentMidSma = midSma.getValue(barCount).doubleValue();
        double lastMidSmaValue = midSma.getValue(barCount - 1).doubleValue();

        Direction direction = trendDirection.get();

        if (currentShortSma > currentMidSma && lastShortSmaValue < lastMidSmaValue && Direction.BUY.equals(direction)) {

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(entryParameter.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitDistanceToLevel(entryParameter.currentPrice(), limitDistance, Direction.BUY)))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopDistanceToLevel(entryParameter.currentPrice(), stopDistance, Direction.BUY))));
        } else if (currentShortSma < currentMidSma && lastShortSmaValue > lastMidSmaValue && Direction.SELL.equals(direction)) {

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(Direction.SELL).asMarketOrder().withPair(entryParameter.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitDistanceToLevel(entryParameter.currentPrice(), limitDistance, Direction.SELL)))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopDistanceToLevel(entryParameter.currentPrice(), stopDistance, Direction.SELL))));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }

    private Optional<Direction> getTrendDirection() {
        int barCount = barSeries.getEndIndex();
        if (barCount < minSlopeWindow) {
            return Optional.empty();
        }

        double current = longSma.getValue(barCount).doubleValue();
        double last = longSma.getValue(barCount - minSlopeWindow).doubleValue();

        double slope = (current - last) / minSlopeWindow;
        if (minSlope.negate().isGreaterThanOrEqualTo(slope)) {
            return Optional.of(Direction.SELL);
        } else if (minSlope.isLessThanOrEqualTo(slope)) {
            return Optional.of(Direction.BUY);
        }
        return Optional.empty();
    }


}
