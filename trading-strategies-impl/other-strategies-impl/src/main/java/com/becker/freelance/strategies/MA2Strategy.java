package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.algorithm.SwingDetection;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.util.List;
import java.util.Optional;

public class MA2Strategy extends BaseStrategy {


    private final int swingHighLowMaxAge;
    private final int swingHighLowOrder;
    private final SwingDetection swingDetection;
    private final SMAIndicator shortSma;
    private final SMAIndicator longSma;

    public MA2Strategy(StrategyParameter parameter, int shortMaPeriod, int longMaPeriod, int swingHighLowMaxAge, int swingHighLowOrder) {
        super(parameter);

        this.swingHighLowMaxAge = swingHighLowMaxAge;
        this.swingHighLowOrder = swingHighLowOrder;
        this.swingDetection = new SwingDetection();
        barSeries.setMaximumBarCount(Math.max(longMaPeriod, swingHighLowOrder));
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        shortSma = new SMAIndicator(closePriceIndicator, shortMaPeriod);
        longSma = new SMAIndicator(closePriceIndicator, longMaPeriod);
    }

    private LastTwoMaResults lastTwoMaValuesForTime(SMAIndicator smaIndicator, int barCount) {
        double last = smaIndicator.getValue(barCount - 2).doubleValue();
        double current = smaIndicator.getValue(barCount - 1).doubleValue();
        return new LastTwoMaResults(last, current);
    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryExecutionParameter entryParameter) {

        int barCount = barSeries.getBarCount();
        LastTwoMaResults lastShortMaValues = lastTwoMaValuesForTime(shortSma, barCount);
        LastTwoMaResults lastLongMaValues = lastTwoMaValuesForTime(longSma, barCount);

        int swingDataCount = swingHighLowMaxAge + swingHighLowOrder;
        Optional<List<TimeSeriesEntry>> optionalSwingHighLowData = entryParameter.timeSeries().getLastNCloseForTimeAsEntryIfExist(entryParameter.time(), swingDataCount);

        if (optionalSwingHighLowData.isEmpty()) {
            return Optional.empty();
        }
        return toEntrySignal(lastShortMaValues, lastLongMaValues, optionalSwingHighLowData.get(), swingHighLowOrder, entryParameter.currentPrice());
    }

    private Optional<EntrySignal> toEntrySignal(LastTwoMaResults lastShortMaValues, LastTwoMaResults lastLongMaValues, List<TimeSeriesEntry> swingData, int swingOrder, TimeSeriesEntry current) {
        Double lastShort = lastShortMaValues.last();
        Double currentShort = lastShortMaValues.current();
        Double lastLong = lastLongMaValues.last();
        Double currentLong = lastLongMaValues.current();

        if (lastShort < lastLong && currentShort > currentLong) {
            //BUY
            Optional<TimeSeriesEntry> lastSwingLow = swingDetection.getLastSwingLow(swingData, swingOrder);
            Pair pair = current.pair();
            return lastSwingLow.map(swingValue -> swingValue.getCloseMid().subtract(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(50), Decimal.ONE)))
                    .map(stopLevel -> entrySignalFactory.fromLevel(Decimal.ONE, Direction.BUY, stopLevel, current.getCloseMid().add(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(150), Decimal.ONE)), PositionBehaviour.HARD_LIMIT, current, currentMarketRegime()));
        } else if (lastShort > lastLong && currentShort < currentLong) {
            //SELL
            Optional<TimeSeriesEntry> lastSwingHigh = swingDetection.getLastSwingHigh(swingData, swingOrder);
            Pair pair = current.pair();
            return lastSwingHigh.map(swingValue -> swingValue.getCloseMid().add(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(50), Decimal.ONE)))
                    .map(stopLevel -> entrySignalFactory.fromLevel(Decimal.ONE, Direction.BUY, stopLevel, current.getCloseMid().subtract(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(150), Decimal.ONE)), PositionBehaviour.HARD_LIMIT, current, currentMarketRegime()));
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
