package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.RSIIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;

public class RsiOverboughtOversoldStrategy extends BaseStrategy{

    public RsiOverboughtOversoldStrategy(){
        super("Rsi_Overbought_Oversold", new PermutableStrategyParameter(
                new StrategyParameter("rsi_period", 12, 5, 17, 1),
                new StrategyParameter("stop_in_euros", 90, 50, 150, 20),
                new StrategyParameter("limit_in_euros", 110, 90, 220, 20),
                new StrategyParameter("size", 0.5, 0.2, 1., 0.2)
            ));
    }

    private BarSeries barSeries;
    private RSIIndicator rsiIndicator;
    private Decimal size;
    private Decimal limitInEuros;
    private Decimal stopInEuros;


    public RsiOverboughtOversoldStrategy(Map<String, Decimal> parameters) {
        this();
        barSeries = new BaseBarSeries();
        int rsiPeriod = parameters.get("rsi_period").intValue();
        barSeries.setMaximumBarCount(rsiPeriod + 1);
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        rsiIndicator = new RSIIndicator(closePriceIndicator, rsiPeriod);
        size = parameters.get("size");
        limitInEuros = parameters.get("limit_in_euros");
        stopInEuros = parameters.get("stop_in_euros");
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new RsiOverboughtOversoldStrategy(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {

        Bar currentBar = timeSeries.getEntryForTimeAsBar(time);
        barSeries.addBar(currentBar);

        int barCount = barSeries.getBarCount();
        double value = rsiIndicator.getValue(barCount - 1).doubleValue();

        TimeSeriesEntry currentEntry = timeSeries.getEntryForTime(time);
        TimeSeriesEntry lastEntry = timeSeries.getLastEntryForTime(time);

        if (value > 70 && isBearishEngulfing(currentEntry, lastEntry)){
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.SELL, stopInEuros, limitInEuros, PositionType.HARD_LIMIT, timeSeries.getEntryForTime(time)));
        } else if (value < 30 && isBullishEngulfing(currentEntry, lastEntry)) {
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.BUY, stopInEuros, limitInEuros, PositionType.HARD_LIMIT, timeSeries.getEntryForTime(time)));
        }

        return Optional.empty();
    }

    private boolean isBullishEngulfing(TimeSeriesEntry currentEntry, TimeSeriesEntry lastEntry){
        return currentEntry.isGreenCandle() && !lastEntry.isGreenCandle() && lastEntry.getHighMid().isLessThan(currentEntry.getCloseMid()) && lastEntry.getLowMid().isGreaterThan(currentEntry.getOpenMid());
    }

    private boolean isBearishEngulfing(TimeSeriesEntry currentEntry, TimeSeriesEntry lastEntry){
        return !currentEntry.isGreenCandle() && lastEntry.isGreenCandle() && lastEntry.getHighMid().isLessThan(currentEntry.getOpenMid()) && lastEntry.getLowMid().isGreaterThan(currentEntry.getCloseMid());
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }
}
