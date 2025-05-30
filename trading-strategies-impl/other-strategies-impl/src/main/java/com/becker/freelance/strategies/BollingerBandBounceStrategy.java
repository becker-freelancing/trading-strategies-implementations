package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.EntrySignalFactory;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.init.PermutableStrategyInitParameter;
import com.becker.freelance.strategies.init.StrategyInitParameter;
import com.becker.freelance.strategies.parameter.EntryParameter;
import com.becker.freelance.strategies.parameter.ExitParameter;
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

import java.util.Map;
import java.util.Optional;

public class BollingerBandBounceStrategy extends BaseStrategy {

    public BollingerBandBounceStrategy() {
        super("Bollinger_Band_Bounce", new PermutableStrategyInitParameter(
                new StrategyInitParameter("period", 14, 10, 25, 1),
                new StrategyInitParameter("std", 2, 1.5, 3.0, 0.5),
                new StrategyInitParameter("size", 0.5, 0.2, 1., 0.2)
        ));
    }

    private int period;
    private Decimal std;
    private Decimal size;
    private BarSeries barSeries;
    private ClosePriceIndicator bandData;
    private SMAIndicator smaIndicator;
    private StandardDeviationIndicator standardDeviationIndicator;

    private BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator;
    private BollingerBandsUpperIndicator bollingerBandsUpperIndicator;
    private BollingerBandsLowerIndicator bollingerBandsLowerIndicator;
    private EntrySignalFactory entrySignalFactory;

    public BollingerBandBounceStrategy(Map<String, Decimal> parameters) {
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
        entrySignalFactory = new EntrySignalFactory();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new BollingerBandBounceStrategy(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {

        Bar currentBar = entryParameter.currentPriceAsBar();
        barSeries.addBar(currentBar);

        TimeSeriesEntry currentPrice = entryParameter.currentPrice();

        Optional<EntrySignal> buyEntrySignal = toBuyEntrySignal(barSeries, bollingerBandsLowerIndicator, bollingerBandsMiddleIndicator, currentPrice, size);
        if (buyEntrySignal.isPresent()) {
            return buyEntrySignal;
        }

        Optional<EntrySignal> sellEntrySignal = toSellEntrySignal(barSeries, bollingerBandsUpperIndicator, bollingerBandsMiddleIndicator, currentPrice, size);
        return sellEntrySignal;
    }

    private Optional<EntrySignal> toBuyEntrySignal(BarSeries series, BollingerBandsLowerIndicator bollingerBandsLowerIndicator, BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator, TimeSeriesEntry currentPrice, Decimal size) {
        int barCount = series.getBarCount();
        Num lowValueNum = bollingerBandsLowerIndicator.getValue(barCount - 1);
        Decimal lowValue = new Decimal(lowValueNum.doubleValue());
        Decimal closeMid = currentPrice.getCloseMid();
        if (currentPrice.getOpenMid().isLessThan(lowValue) && closeMid.isGreaterThan(lowValue)) {
            Num middleValueNum = bollingerBandsMiddleIndicator.getValue(barCount - 1);
            Decimal middleValue = new Decimal(middleValueNum.doubleValue());
            Pair pair = currentPrice.pair();
            Decimal stop = lowValue.subtract(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal("50"), size));
            return Optional.of(entrySignalFactory.fromLevel(size, Direction.BUY, stop, middleValue, PositionType.TRAILING, currentPrice));
        }
        return Optional.empty();
    }

    private Optional<EntrySignal> toSellEntrySignal(BarSeries series, BollingerBandsUpperIndicator bollingerBandsUpperIndicator, BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator, TimeSeriesEntry currentPrice, Decimal size) {
        int barCount = series.getBarCount();
        Decimal highValue = new Decimal(bollingerBandsUpperIndicator.getValue(barCount - 1).doubleValue());
        Decimal closeMid = currentPrice.getCloseMid();
        if (currentPrice.getOpenMid().isGreaterThan(highValue) && closeMid.isLessThan(highValue)) {
            Decimal middleValue = new Decimal(bollingerBandsMiddleIndicator.getValue(barCount - 1).doubleValue());
            Pair pair = currentPrice.pair();
            Decimal stop = highValue.add(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal("50"), size));
            return Optional.of(entrySignalFactory.fromLevel(size, Direction.SELL, stop, middleValue, PositionType.TRAILING, currentPrice));
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }
}
