package com.becker.freelance.strategies.classification;

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

public class ClassificationStrategy extends BaseStrategy {

    private final Double minProbabilityForEntry;
    private final Double takeProfitDelta;
    private final Double stopLossDelta;
    private final PositionBehaviour positionBehaviour;
    private final ClassificationPredictor classificationPredictor;

    public ClassificationStrategy(StrategyParameter strategyParameter, Double minProbabilityForEntry, Double takeProfitDelta, Double stopLossDelta, PositionBehaviour positionBehaviour, ClassificationPredictor classificationPredictor) {
        super(strategyParameter);
        this.minProbabilityForEntry = minProbabilityForEntry;
        this.takeProfitDelta = takeProfitDelta;
        this.stopLossDelta = stopLossDelta;
        this.positionBehaviour = positionBehaviour;
        this.classificationPredictor = classificationPredictor;
    }

    @Override
    protected Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {
        Optional<ClassificationPrediction> prediction = classificationPredictor.predict(entryParameter, null);
        return prediction.flatMap(pred -> toEntrySignal(pred, entryParameter.currentPrice()));
    }

    private Optional<EntrySignalBuilder> toEntrySignal(ClassificationPrediction classificationPrediction, TimeSeriesEntry currentPrice) {
        if (classificationPrediction.maxProbabilityForBuyAndSell() > minProbabilityForEntry) {
            if (classificationPrediction.buyProbability() > minProbabilityForEntry) {
                Direction direction = Direction.BUY;
                Decimal price = currentPrice.getClosePriceForDirection(direction);
                entrySignalBuilder()
                        .withPositionBehaviour(positionBehaviour)
                        .withOpenMarketRegime(currentMarketRegime())
                        .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(direction))
                        .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(price.subtract(stopLossDelta)))
                        .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(price.add(takeProfitDelta)));
            } else if (classificationPrediction.sellProbability() > minProbabilityForEntry) {
                Direction direction = Direction.SELL;
                Decimal price = currentPrice.getClosePriceForDirection(direction);
                entrySignalBuilder()
                        .withPositionBehaviour(positionBehaviour)
                        .withOpenMarketRegime(currentMarketRegime())
                        .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(direction))
                        .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(price.add(stopLossDelta)))
                        .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(price.subtract(takeProfitDelta)));

            }
        }

        return Optional.empty();
    }

    @Override
    protected Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }
}
