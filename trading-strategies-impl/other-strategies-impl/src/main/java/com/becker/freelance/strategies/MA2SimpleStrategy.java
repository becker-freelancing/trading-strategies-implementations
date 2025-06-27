package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
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
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.util.Optional;

public class MA2SimpleStrategy extends BaseStrategy {


    private final SMAIndicator shortSma;
    private final SMAIndicator longSma;

    public MA2SimpleStrategy(StrategyParameter parameter, int shortMaPeriod, int longMaPeriod) {
        super(parameter);
        barSeries.setMaximumBarCount(longMaPeriod + 5);
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        shortSma = new SMAIndicator(closePriceIndicator, shortMaPeriod);
        longSma = new SMAIndicator(closePriceIndicator, longMaPeriod);
    }

    private LastTwoMaResults lastTwoMaValuesForTime(SMAIndicator smaIndicator, int barCount) {
        double last = smaIndicator.getValue(barCount - 1).doubleValue();
        double current = smaIndicator.getValue(barCount).doubleValue();
        return new LastTwoMaResults(last, current);
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        int barCount = barSeries.getEndIndex();
        LastTwoMaResults lastShortMaValues = lastTwoMaValuesForTime(shortSma, barCount);
        LastTwoMaResults lastLongMaValues = lastTwoMaValuesForTime(longSma, barCount);

        return toEntrySignal(lastShortMaValues, lastLongMaValues, entryParameter.currentPrice());
    }

    private Optional<EntrySignalBuilder> toEntrySignal(LastTwoMaResults lastShortMaValues, LastTwoMaResults lastLongMaValues, TimeSeriesEntry current) {
        Double lastShort = lastShortMaValues.last();
        Double currentShort = lastShortMaValues.current();
        Double lastLong = lastLongMaValues.last();
        Double currentLong = lastLongMaValues.current();

        if (lastShort < lastLong && currentShort > currentLong) {
            //BUY
            Pair pair = current.pair();
            return Optional.ofNullable(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(current.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(current.getCloseMid().add(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(150), Decimal.ONE))))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(current.getCloseMid().subtract(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(50), Decimal.ONE)))));

        } else if (lastShort > lastLong && currentShort < currentLong) {
            //SELL
            Pair pair = current.pair();
            return Optional.ofNullable(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                    .withOpenOrder(orderBuilder().withDirection(Direction.SELL).asMarketOrder().withPair(current.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(current.getCloseMid().subtract(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(150), Decimal.ONE))))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(current.getCloseMid().add(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(50), Decimal.ONE)))));
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }

    private record LastTwoMaResults(Double last, Double current) {
    }
}
