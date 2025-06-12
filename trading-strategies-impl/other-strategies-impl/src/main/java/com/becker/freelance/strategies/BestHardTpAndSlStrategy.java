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

import java.util.Optional;

public class BestHardTpAndSlStrategy extends BaseStrategy {

    private final Direction direction;
    private final Decimal tp;
    private final Decimal sl;

    public BestHardTpAndSlStrategy(StrategyParameter parameter, boolean allBuy, Decimal tp, Decimal sl) {
        super(parameter);
        this.direction = allBuy ? Direction.BUY : Direction.SELL;
        this.tp = tp;
        this.sl = sl;
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        return Optional.of(entrySignalBuilder()
                .withOpenMarketRegime(currentMarketRegime())
                .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                .withOpenOrder(orderBuilder().asMarketOrder().withDirection(direction).withPair(entryParameter.pair()))
                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(tpPrice(entryParameter.currentPrice())))
                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(slPrice(entryParameter.currentPrice()))));
    }

    private Decimal tpPrice(TimeSeriesEntry currentPrice) {
        return switch (direction) {
            case BUY -> currentPrice.getClosePriceForDirection(direction).add(tp);
            case SELL -> currentPrice.getClosePriceForDirection(direction).subtract(tp);
        };
    }

    private Decimal slPrice(TimeSeriesEntry currentPrice) {
        return switch (direction) {
            case BUY -> currentPrice.getClosePriceForDirection(direction).subtract(sl);
            case SELL -> currentPrice.getClosePriceForDirection(direction).add(sl);
        };
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }

}
