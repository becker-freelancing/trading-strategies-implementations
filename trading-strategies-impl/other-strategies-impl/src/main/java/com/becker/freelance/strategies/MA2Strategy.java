package com.becker.freelance.strategies;

import com.becker.freelance.commons.*;
import com.becker.freelance.strategies.algorithm.SwingDetection;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class MA2Strategy extends BaseStrategy{

    private static boolean shortMaLessThanLongMaValidation(Map<String, Double> parameter){
        return parameter.get("short_ma_period") < parameter.get("long_ma_period");
    }

    private static record LastTwoMaResults(Double last, Double current){}


    public MA2Strategy() {
        super("2_MA_Strategy", new PermutableStrategyParameter(List.of(
                new StrategyParameter("short_ma_period", 5, 1, 10, 1),
                new StrategyParameter("long_ma_period", 20, 2, 20, 1),
                new StrategyParameter("swing_high_low_order", 2, 1, 10, 1),
                new StrategyParameter("swing_high_low_max_age", 10, 5, 45, 10)
        ), MA2Strategy::shortMaLessThanLongMaValidation));

    }

    private int swingHighLowMaxAge;
    private int swingHighLowOrder;
    private SwingDetection swingDetection;
    private BarSeries barSeries;
    private SMAIndicator shortSma;
    private SMAIndicator longSma;

    public MA2Strategy(Map<String, Double> parameters) {
        super(parameters);

        int shortPeriod = parameters.get("short_ma_period").intValue();
        int longPeriod = parameters.get("long_ma_period").intValue();
        swingHighLowMaxAge = parameters.get("swing_high_low_max_age").intValue();
        swingHighLowOrder = parameters.get("swing_high_low_order").intValue();
        this.swingDetection = new SwingDetection();
        barSeries = new BaseBarSeries();
        barSeries.setMaximumBarCount(Math.max(longPeriod, swingHighLowOrder));
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        shortSma = new SMAIndicator(closePriceIndicator, shortPeriod);
        longSma = new SMAIndicator(closePriceIndicator, longPeriod);
    }

    @Override
    public BaseStrategy forParameters(Map<String, Double> parameters) {
        return new MA2Strategy(parameters);
    }

    @Override
    public int minNumberOfBarsRequired(Map<String, Double> parameters) {
        int swingHighLowMaxAge = parameters.get("swing_high_low_max_age").intValue();
        int swingHighLowOrder = parameters.get("swing_high_low_order").intValue();
        return swingHighLowOrder + swingHighLowMaxAge;
    }

    private LastTwoMaResults lastTwoMaValuesForTime(SMAIndicator smaIndicator, int barCount){
        double last = smaIndicator.getValue(barCount - 2).doubleValue();
        double current = smaIndicator.getValue(barCount - 1).doubleValue();
        return new LastTwoMaResults(last, current);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Bar currentPrice = timeSeries.getEntryForTimeAsBar(time);
        barSeries.addBar(currentPrice);
        int barCount = barSeries.getBarCount();
        LastTwoMaResults lastShortMaValues = lastTwoMaValuesForTime(shortSma, barCount);
        LastTwoMaResults lastLongMaValues = lastTwoMaValuesForTime(longSma, barCount);

        List<TimeSeriesEntry> swingHighLowData = timeSeries.getLastNCloseForTimeAsEntry(time, swingHighLowMaxAge + swingHighLowOrder);

        return toEntrySignal(lastShortMaValues, lastLongMaValues, swingHighLowData, swingHighLowOrder, timeSeries.getEntryForTime(time));
    }

    private Optional<EntrySignal> toEntrySignal(LastTwoMaResults lastShortMaValues, LastTwoMaResults lastLongMaValues, List<TimeSeriesEntry> swingData, int swingOrder, TimeSeriesEntry current) {
        Double lastShort = lastShortMaValues.last();
        Double currentShort = lastShortMaValues.current();
        Double lastLong = lastLongMaValues.last();
        Double currentLong = lastLongMaValues.current();

        if (lastShort < lastLong && currentShort > currentLong){
            //BUY
            Optional<TimeSeriesEntry> lastSwingLow = swingDetection.getLastSwingLow(swingData, swingOrder);
            double stopPoints = lastSwingLow.map(entry -> Math.round(Math.abs(current.closeMid() - entry.closeMid()) + 5)).orElse(10L);
            return Optional.of(new EntrySignal(1, Direction.BUY, stopPoints, 15, PositionType.HARD_LIMIT));
        } else if (lastShort > lastLong && currentShort < currentLong) {
            //SELL
            Optional<TimeSeriesEntry> lastSwingLow = swingDetection.getLastSwingHigh(swingData, swingOrder);
            double stopPoints = lastSwingLow.map(entry -> Math.round(Math.abs(current.closeMid() - entry.closeMid()) + 5)).orElse(10L);
            return Optional.of(new EntrySignal(1, Direction.SELL, stopPoints, 15, PositionType.HARD_LIMIT));
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }
}
