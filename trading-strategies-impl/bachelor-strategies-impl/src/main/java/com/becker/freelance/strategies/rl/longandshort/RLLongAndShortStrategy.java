package com.becker.freelance.strategies.rl.longandshort;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.Position;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.rl.read.RLAction;
import com.becker.freelance.strategies.rl.read.RLPrediction;
import com.becker.freelance.strategies.rl.read.RLPredictor;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;

import java.util.Optional;

public abstract class RLLongAndShortStrategy extends BaseStrategy {

    private final RLPredictor rlPredictor;
    private final PositionBehaviour positionBehaviour;

    private RLPrediction currentPrediction;

    protected RLLongAndShortStrategy(StrategyParameter strategyParameter, RLPredictor rlPredictor, PositionBehaviour positionBehaviour) {
        super(strategyParameter);
        this.rlPredictor = rlPredictor;
        this.positionBehaviour = positionBehaviour;
    }

    protected abstract Decimal getStopDistance();

    protected abstract Decimal getLimitDistance(Decimal stopDistance);

    @Override
    protected Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {
        return Optional.ofNullable(currentPrediction)
                .flatMap(prediction -> toEntrySignal(prediction, entryParameter.currentPrice()));
    }

    protected Optional<EntrySignalBuilder> toEntrySignal(RLPrediction prediction, TimeSeriesEntry currentPrice) {
        if (prediction.rlAction() == RLAction.BUY) {
            return toBuyEntrySignal(currentPrice);
        } else if (prediction.rlAction() == RLAction.SELL) {
            return toSellEntrySignal(currentPrice);
        }
        return Optional.empty();
    }

    private Optional<EntrySignalBuilder> toBuyEntrySignal(TimeSeriesEntry currentPrice) {
        Direction direction = Direction.BUY;
        Decimal price = currentPrice.getClosePriceForDirection(direction);
        Decimal stopDistance = getStopDistance();
        Decimal limitDistance = getLimitDistance(stopDistance);
        return Optional.of(entrySignalBuilder()
                .withPositionBehaviour(positionBehaviour)
                .withOpenMarketRegime(currentMarketRegime())
                .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(direction))
                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(price.subtract(stopDistance)))
                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(price.add(limitDistance))));
    }

    private Optional<EntrySignalBuilder> toSellEntrySignal(TimeSeriesEntry currentPrice) {
        Direction direction = Direction.SELL;
        Decimal price = currentPrice.getClosePriceForDirection(direction);
        Decimal stopDistance = getStopDistance();
        Decimal limitDistance = getLimitDistance(stopDistance);
        return Optional.of(entrySignalBuilder()
                .withPositionBehaviour(positionBehaviour)
                .withOpenMarketRegime(currentMarketRegime())
                .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(direction))
                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(price.add(stopDistance)))
                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(price.subtract(limitDistance))));
    }


    @Override
    protected Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        this.currentPrediction = rlPredictor.predict(exitParameter, null).orElse(null);

        if (currentPrediction == null) {
            return Optional.empty();
        }

        if (currentPrediction.rlAction() == RLAction.LIQUIDATE) {

            Optional<Direction> direction = getOpenPositionRequestor().getOpenPositions().stream()
                    .filter(position -> position.getPair().equals(getPair()))
                    .map(Position::getDirection)
                    .findAny();
            return direction.map(ExitSignal::new);
        }

        return Optional.empty();
    }
}
