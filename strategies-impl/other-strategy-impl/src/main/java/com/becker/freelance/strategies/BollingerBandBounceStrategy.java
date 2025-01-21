package com.becker.freelance.strategies;

import com.becker.freelance.commons.*;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsLowerIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsMiddleIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsUpperIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;
import org.ta4j.core.indicators.statistics.StandardDeviationIndicator;
import org.ta4j.core.num.DecimalNum;
import org.ta4j.core.num.Num;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;

public class BollingerBandBounceStrategy extends BaseStrategy {

    public BollingerBandBounceStrategy() {
        super("Bollinger_Band_Bounce", new PermutableStrategyParameter(
                new StrategyParameter("period", 14, 10, 25, 1),
                new StrategyParameter("std", 2, 1.5, 3.0, 0.5),
                new StrategyParameter("size", 0.5, 0.2, 1, 0.2)
        ));
    }

    private int period;
    private Double std;
    private Double size;
    private BarSeries barSeries;
    private ClosePriceIndicator bandData;
    private SMAIndicator smaIndicator;
    private StandardDeviationIndicator standardDeviationIndicator;

    private BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator;
    private BollingerBandsUpperIndicator bollingerBandsUpperIndicator;
    private BollingerBandsLowerIndicator bollingerBandsLowerIndicator;

    public BollingerBandBounceStrategy(Map<String, Double> parameters) {
        super(parameters);
        period = parameters.get("period").intValue();
        std = parameters.get("std");
        size = parameters.get("size");
        barSeries = new BaseBarSeries();
        bandData = new ClosePriceIndicator(barSeries);
        smaIndicator = new SMAIndicator(bandData, period);
        standardDeviationIndicator = new StandardDeviationIndicator(bandData, period);
        bollingerBandsMiddleIndicator = new BollingerBandsMiddleIndicator(smaIndicator);
        bollingerBandsUpperIndicator = new BollingerBandsUpperIndicator(bollingerBandsMiddleIndicator, standardDeviationIndicator, DecimalNum.valueOf(std));
        bollingerBandsLowerIndicator = new BollingerBandsLowerIndicator(bollingerBandsMiddleIndicator, standardDeviationIndicator, DecimalNum.valueOf(std));
    }

    @Override
    public BaseStrategy forParameters(Map<String, Double> parameters) {
        return new BollingerBandBounceStrategy(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {

        Bar currentBar = timeSeries.getEntryForTimeAsBar(time);
        barSeries.addBar(currentBar);

        TimeSeriesEntry currentPrice = timeSeries.getEntryForTime(time);

        Optional<EntrySignal> buyEntrySignal = toBuyEntrySignal(barSeries, bollingerBandsLowerIndicator, bollingerBandsMiddleIndicator, currentPrice, size);
        if (buyEntrySignal.isPresent()) {
            return buyEntrySignal;
        }

        Optional<EntrySignal> sellEntrySignal = toSellEntrySignal(barSeries, bollingerBandsUpperIndicator, bollingerBandsMiddleIndicator, currentPrice, size);
        return sellEntrySignal;
    }

    private Optional<EntrySignal> toBuyEntrySignal(BarSeries series, BollingerBandsLowerIndicator bollingerBandsLowerIndicator, BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator, TimeSeriesEntry currentPrice, Double size) {
        int barCount = series.getBarCount();
        Num lowValueNum = bollingerBandsLowerIndicator.getValue(barCount - 1);
        double lowValue = lowValueNum.doubleValue();
        double closeMid = currentPrice.closeMid();
        if (currentPrice.openMid() < lowValue && closeMid > lowValue) {
            Num middleValueNum = bollingerBandsMiddleIndicator.getValue(barCount - 1);
            double middleValue = middleValueNum.doubleValue();
            double limit = Math.abs(closeMid - middleValue);
            double stop = Math.abs(closeMid - lowValue) + 5;
            return Optional.of(new EntrySignal(size, Direction.BUY, stop, limit, PositionType.HARD_LIMIT));
        }
        return Optional.empty();
    }

    private Optional<EntrySignal> toSellEntrySignal(BarSeries series, BollingerBandsUpperIndicator bollingerBandsUpperIndicator, BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator, TimeSeriesEntry currentPrice, Double size) {
        int barCount = series.getBarCount();
        double highValue = bollingerBandsUpperIndicator.getValue(barCount - 1).doubleValue();
        double closeMid = currentPrice.closeMid();
        if (currentPrice.openMid() > highValue && closeMid < highValue) {
            double middleValue = bollingerBandsMiddleIndicator.getValue(barCount - 1).doubleValue();
            double limit = Math.abs(closeMid - middleValue);
            double stop = Math.abs(closeMid - highValue) + 5;
            return Optional.of(new EntrySignal(size, Direction.BUY, stop, limit, PositionType.HARD_LIMIT));
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }
}
