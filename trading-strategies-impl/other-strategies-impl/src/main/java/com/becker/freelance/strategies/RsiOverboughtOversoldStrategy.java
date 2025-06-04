package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignal;
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
    private final Decimal size;
    private final Decimal limitInEuros;
    private final Decimal stopInEuros;


    public RsiOverboughtOversoldStrategy(StrategyParameter parameter, int rsiPeriod, Decimal size, Decimal limit, Decimal stop) {
        super(parameter);
        barSeries.setMaximumBarCount(rsiPeriod + 1);
        rsiIndicator = new RSIIndicator(closePrice, rsiPeriod);
        this.size = size;
        this.limitInEuros = limit;
        this.stopInEuros = stop;
    }


    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryExecutionParameter entryParameter) {

        int barCount = barSeries.getBarCount();
        double value = rsiIndicator.getValue(barCount - 1).doubleValue();

        TimeSeriesEntry currentEntry = entryParameter.currentPrice();
        TimeSeriesEntry lastEntry = entryParameter.timeSeries().getLastEntryForTime(entryParameter.time());

        if (value > 70 && isBearishEngulfing(currentEntry, lastEntry)) {
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.SELL, stopInEuros, limitInEuros, PositionBehaviour.HARD_LIMIT, entryParameter.currentPrice(), currentMarketRegime()));
        } else if (value < 30 && isBullishEngulfing(currentEntry, lastEntry)) {
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.BUY, stopInEuros, limitInEuros, PositionBehaviour.HARD_LIMIT, entryParameter.currentPrice(), currentMarketRegime()));
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
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }
}
