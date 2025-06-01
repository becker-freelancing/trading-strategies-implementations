package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;
import org.ta4j.core.indicators.RSIIndicator;

import java.util.Optional;

public class RsiOverboughtOversoldStrategy extends BaseStrategy {


    private final RSIIndicator rsiIndicator;
    private final Decimal size;
    private final Decimal limitInEuros;
    private final Decimal stopInEuros;


    public RsiOverboughtOversoldStrategy(StrategyCreator strategyCreator, int rsiPeriod, Decimal size, Decimal limit, Decimal stop) {
        super(strategyCreator);
        barSeries.setMaximumBarCount(rsiPeriod + 1);
        rsiIndicator = new RSIIndicator(closePrice, rsiPeriod);
        this.size = size;
        this.limitInEuros = limit;
        this.stopInEuros = stop;
    }


    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {

        int barCount = barSeries.getBarCount();
        double value = rsiIndicator.getValue(barCount - 1).doubleValue();

        TimeSeriesEntry currentEntry = entryParameter.currentPrice();
        TimeSeriesEntry lastEntry = entryParameter.timeSeries().getLastEntryForTime(entryParameter.time());

        if (value > 70 && isBearishEngulfing(currentEntry, lastEntry)) {
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.SELL, stopInEuros, limitInEuros, PositionType.HARD_LIMIT, entryParameter.currentPrice()));
        } else if (value < 30 && isBullishEngulfing(currentEntry, lastEntry)) {
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.BUY, stopInEuros, limitInEuros, PositionType.HARD_LIMIT, entryParameter.currentPrice()));
        }

        return Optional.empty();
    }

    private boolean isBullishEngulfing(TimeSeriesEntry currentEntry, TimeSeriesEntry lastEntry) {
        return currentEntry.isGreenCandle() && !lastEntry.isGreenCandle() && lastEntry.getHighMid().isLessThan(currentEntry.getCloseMid()) && lastEntry.getLowMid().isGreaterThan(currentEntry.getOpenMid());
    }

    private boolean isBearishEngulfing(TimeSeriesEntry currentEntry, TimeSeriesEntry lastEntry) {
        return !currentEntry.isGreenCandle() && lastEntry.isGreenCandle() && lastEntry.getHighMid().isLessThan(currentEntry.getOpenMid()) && lastEntry.getLowMid().isGreaterThan(currentEntry.getCloseMid());
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }
}
