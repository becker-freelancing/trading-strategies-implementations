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
import org.ta4j.core.indicators.EMAIndicator;
import org.ta4j.core.indicators.MACDIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.util.Optional;

public class MACDScalping extends BaseStrategy {

    private final MACDIndicator macdIndicator;
    private final EMAIndicator macdSignal;
    private final Decimal stopDistance;
    private final Decimal limitDistance;
    private final int longBarCount;

    public MACDScalping(StrategyParameter parameter, int longBarCount, int shortBarCount, int signalLinePeriod, Decimal stop, Decimal limit) {
        super(parameter);

        barSeries.setMaximumBarCount(longBarCount + 3);
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        macdIndicator = new MACDIndicator(closePriceIndicator, shortBarCount, longBarCount);
        macdSignal = new EMAIndicator(macdIndicator, signalLinePeriod);
        stopDistance = stop;
        limitDistance = limit;
        this.longBarCount = longBarCount;
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        int barCount = barSeries.getBarCount();
        if (barCount < longBarCount) {
            return Optional.empty();
        }
        double currentMacd = macdIndicator.getValue(barCount - 1).doubleValue();
        double lastMacd = macdIndicator.getValue(barCount - 2).doubleValue();
        double currentSignal = macdSignal.getValue(barCount - 1).doubleValue();
        double lastSignal = macdSignal.getValue(barCount - 2).doubleValue();

        if (currentMacd > currentSignal && lastMacd < lastSignal) {
            //BUY

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(entryParameter.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitDistanceToLevel(entryParameter.currentPrice(), limitDistance, Direction.BUY)))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopDistanceToLevel(entryParameter.currentPrice(), stopDistance, Direction.BUY))));
        } else if (currentMacd < currentSignal && lastMacd > lastSignal) {
            //SELL

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

}
