package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.indicators.ta.swing.SwingHighIndicator;
import com.becker.freelance.indicators.ta.swing.SwingHighPoint;
import com.becker.freelance.indicators.ta.swing.SwingLowIndicator;
import com.becker.freelance.indicators.ta.swing.SwingLowPoint;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import org.ta4j.core.Indicator;

import java.util.Optional;

public class SwingHighLowStrategy extends BaseStrategy {


    private final Indicator<Optional<SwingHighPoint>> swingHighIndicator;
    private final Indicator<Optional<SwingLowPoint>> swingLowIndicator;
    private final Decimal stopDistance;
    private final Decimal limitDistance;
    private SwingHighPoint lastSwingHighOrNull;
    private SwingLowPoint lastSwingLowOrNull;
    private int index;


    public SwingHighLowStrategy(StrategyParameter parameter, int swingPeriod, Decimal stopDistance, Decimal limitDistance) {
        super(parameter);

        swingHighIndicator = new SwingHighIndicator(swingPeriod, closePrice);
        swingLowIndicator = new SwingLowIndicator(swingPeriod, closePrice);
        this.stopDistance = stopDistance;
        this.limitDistance = limitDistance;
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        if (lastSwingLowOrNull == null || lastSwingHighOrNull == null) {
            return Optional.empty();
        }

        if (lastSwingHighOrNull.index() == index - 1) {

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(Direction.SELL).asMarketOrder().withPair(entryParameter.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitDistanceToLevel(entryParameter.currentPrice(), limitDistance, Direction.SELL)))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopDistanceToLevel(entryParameter.currentPrice(), stopDistance, Direction.SELL))));
        } else if (lastSwingLowOrNull.index() == index - 1) {

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(entryParameter.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitDistanceToLevel(entryParameter.currentPrice(), limitDistance, Direction.BUY)))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopDistanceToLevel(entryParameter.currentPrice(), stopDistance, Direction.BUY))));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        updateData();

        if (lastSwingLowOrNull == null || lastSwingHighOrNull == null) {
            return Optional.empty();
        }

        if (lastSwingHighOrNull.index() == index - 1) {
            return Optional.of(new ExitSignal(Direction.BUY));
        } else if (lastSwingLowOrNull.index() == index - 1) {
            return Optional.of(new ExitSignal(Direction.SELL));
        }

        return Optional.empty();
    }

    private void updateData() {
        index = barSeries.getEndIndex();

        Optional<SwingLowPoint> optionalSwingLowPoint = swingLowIndicator.getValue(index);
        Optional<SwingHighPoint> optionalSwingHighPoint = swingHighIndicator.getValue(index);

        lastSwingHighOrNull = optionalSwingHighPoint.orElse(null);
        lastSwingLowOrNull = optionalSwingLowPoint.orElse(null);
    }
}
