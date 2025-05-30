package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.algorithm.SwingDetection;
import com.becker.freelance.strategies.init.PermutableStrategyInitParameter;
import com.becker.freelance.strategies.init.StrategyInitParameter;
import com.becker.freelance.strategies.parameter.EntryParameter;
import com.becker.freelance.strategies.parameter.ExitParameter;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.util.List;
import java.util.Map;
import java.util.Optional;

public class MA2Strategy extends BaseStrategy{

    private static boolean shortMaLessThanLongMaValidation(Map<String, Decimal> parameter){
        return parameter.get("short_ma_period").isLessThan(parameter.get("long_ma_period"));
    }

    private record LastTwoMaResults(Double last, Double current) {
    }


    public MA2Strategy() {
        super("2_MA_Strategy", new PermutableStrategyInitParameter(List.of(
                new StrategyInitParameter("short_ma_period", 5, 1, 10, 1),
                new StrategyInitParameter("long_ma_period", 20, 2, 20, 1),
                new StrategyInitParameter("swing_high_low_order", 2, 1, 10, 1),
                new StrategyInitParameter("swing_high_low_max_age", 10, 5, 45, 10)
        ), MA2Strategy::shortMaLessThanLongMaValidation));

    }

    private int swingHighLowMaxAge;
    private int swingHighLowOrder;
    private SwingDetection swingDetection;
    private BarSeries barSeries;
    private SMAIndicator shortSma;
    private SMAIndicator longSma;

    public MA2Strategy(Map<String, Decimal> parameters) {
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
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new MA2Strategy(parameters);
    }

    private LastTwoMaResults lastTwoMaValuesForTime(SMAIndicator smaIndicator, int barCount){
        double last = smaIndicator.getValue(barCount - 2).doubleValue();
        double current = smaIndicator.getValue(barCount - 1).doubleValue();
        return new LastTwoMaResults(last, current);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {
        Bar currentPrice = entryParameter.currentPriceAsBar();
        barSeries.addBar(currentPrice);
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

        if (lastShort < lastLong && currentShort > currentLong){
            //BUY
            Optional<TimeSeriesEntry> lastSwingLow = swingDetection.getLastSwingLow(swingData, swingOrder);
            Pair pair = current.pair();
            return lastSwingLow.map(swingValue -> swingValue.getCloseMid().subtract(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(50), Decimal.ONE)))
                    .map(stopLevel -> entrySignalFactory.fromLevel(Decimal.ONE, Direction.BUY, stopLevel, current.getCloseMid().add(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(150), Decimal.ONE)), PositionType.HARD_LIMIT, current));
        } else if (lastShort > lastLong && currentShort < currentLong) {
            //SELL
            Optional<TimeSeriesEntry> lastSwingHigh = swingDetection.getLastSwingHigh(swingData, swingOrder);
            Pair pair = current.pair();
            return lastSwingHigh.map(swingValue -> swingValue.getCloseMid().add(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(50), Decimal.ONE)))
                    .map(stopLevel -> entrySignalFactory.fromLevel(Decimal.ONE, Direction.BUY, stopLevel, current.getCloseMid().subtract(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal(150), Decimal.ONE)), PositionType.HARD_LIMIT, current));
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }
}
