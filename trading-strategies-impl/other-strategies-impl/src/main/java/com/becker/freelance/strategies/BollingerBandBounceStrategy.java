package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;
import org.ta4j.core.BarSeries;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsLowerIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsMiddleIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsUpperIndicator;
import org.ta4j.core.indicators.statistics.StandardDeviationIndicator;
import org.ta4j.core.num.DecimalNum;
import org.ta4j.core.num.Num;

import java.util.Optional;

public class BollingerBandBounceStrategy extends BaseStrategy {


    private final Decimal size;
    private final SMAIndicator smaIndicator;
    private final StandardDeviationIndicator standardDeviationIndicator;

    private final BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator;
    private final BollingerBandsUpperIndicator bollingerBandsUpperIndicator;
    private final BollingerBandsLowerIndicator bollingerBandsLowerIndicator;

    public BollingerBandBounceStrategy(StrategyCreator strategyCreator, int period, Decimal std, Decimal size) {
        super(strategyCreator);
        this.size = size;
        smaIndicator = new SMAIndicator(closePrice, period);
        standardDeviationIndicator = new StandardDeviationIndicator(closePrice, period);
        bollingerBandsMiddleIndicator = new BollingerBandsMiddleIndicator(smaIndicator);
        bollingerBandsUpperIndicator = new BollingerBandsUpperIndicator(bollingerBandsMiddleIndicator, standardDeviationIndicator, DecimalNum.valueOf(std));
        bollingerBandsLowerIndicator = new BollingerBandsLowerIndicator(bollingerBandsMiddleIndicator, standardDeviationIndicator, DecimalNum.valueOf(std));
    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {

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
    public Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }
}
