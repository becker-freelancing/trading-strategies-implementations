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
import org.ta4j.core.BarSeries;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsLowerIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsMiddleIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsUpperIndicator;
import org.ta4j.core.indicators.statistics.StandardDeviationIndicator;
import org.ta4j.core.num.DecimalNum;
import org.ta4j.core.num.Num;

import java.util.Optional;

public class BollingerBandBounceMinSlopeStrategy extends BaseStrategy {


    private final Decimal size;

    private final BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator;
    private final BollingerBandsUpperIndicator bollingerBandsUpperIndicator;
    private final BollingerBandsLowerIndicator bollingerBandsLowerIndicator;

    private final SMAIndicator slopeSma;
    private final int slopeWindow;
    private final Decimal minSlope;


    public BollingerBandBounceMinSlopeStrategy(StrategyParameter parameter, int period, Decimal std, Decimal size, Decimal minSlope, int minSlopeWindow, int minSlopePeriod) {
        super(parameter);
        this.size = size;
        this.minSlope = minSlope;
        this.slopeWindow = minSlopeWindow;

        SMAIndicator smaIndicator = new SMAIndicator(closePrice, period);
        StandardDeviationIndicator standardDeviationIndicator = new StandardDeviationIndicator(closePrice, period);
        bollingerBandsMiddleIndicator = new BollingerBandsMiddleIndicator(smaIndicator);
        bollingerBandsUpperIndicator = new BollingerBandsUpperIndicator(bollingerBandsMiddleIndicator, standardDeviationIndicator, DecimalNum.valueOf(std));
        bollingerBandsLowerIndicator = new BollingerBandsLowerIndicator(bollingerBandsMiddleIndicator, standardDeviationIndicator, DecimalNum.valueOf(std));
        slopeSma = new SMAIndicator(closePrice, minSlopePeriod);
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        if (!isTrend()) {
            return Optional.empty();
        }

        TimeSeriesEntry currentPrice = entryParameter.currentPrice();

        Optional<EntrySignalBuilder> buyEntrySignal = toBuyEntrySignal(barSeries, bollingerBandsLowerIndicator, bollingerBandsMiddleIndicator, currentPrice, size);
        if (buyEntrySignal.isPresent()) {
            return buyEntrySignal;
        }

        Optional<EntrySignalBuilder> sellEntrySignal = toSellEntrySignal(barSeries, bollingerBandsUpperIndicator, bollingerBandsMiddleIndicator, currentPrice, size);
        return sellEntrySignal;
    }

    private boolean isTrend() {
        int barCount = barSeries.getBarCount();
        if (barCount < slopeWindow) {
            return false;
        }

        double current = slopeSma.getValue(barCount - 1).doubleValue();
        double last = slopeSma.getValue(barCount - slopeWindow - 1).doubleValue();

        return minSlope.isLessThanOrEqualTo(Math.abs(current - last));
    }

    private Optional<EntrySignalBuilder> toBuyEntrySignal(BarSeries series, BollingerBandsLowerIndicator bollingerBandsLowerIndicator, BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator, TimeSeriesEntry currentPrice, Decimal size) {
        int barCount = series.getBarCount();
        Num lowValueNum = bollingerBandsLowerIndicator.getValue(barCount - 1);
        Decimal lowValue = new Decimal(lowValueNum.doubleValue());
        Decimal closeMid = currentPrice.getCloseMid();
        if (currentPrice.getOpenMid().isLessThan(lowValue) && closeMid.isGreaterThan(lowValue)) {
            Num middleValueNum = bollingerBandsMiddleIndicator.getValue(barCount - 1);
            Decimal middleValue = new Decimal(middleValueNum.doubleValue());
            Pair pair = currentPrice.pair();
            Decimal stop = lowValue.subtract(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal("50"), size));

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.TRAILING)
                    .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(currentPrice.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(middleValue))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stop)));
        }
        return Optional.empty();
    }

    private Optional<EntrySignalBuilder> toSellEntrySignal(BarSeries series, BollingerBandsUpperIndicator bollingerBandsUpperIndicator, BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator, TimeSeriesEntry currentPrice, Decimal size) {
        int barCount = series.getBarCount();
        Decimal highValue = new Decimal(bollingerBandsUpperIndicator.getValue(barCount - 1).doubleValue());
        Decimal closeMid = currentPrice.getCloseMid();
        if (currentPrice.getOpenMid().isGreaterThan(highValue) && closeMid.isLessThan(highValue)) {
            Decimal middleValue = new Decimal(bollingerBandsMiddleIndicator.getValue(barCount - 1).doubleValue());
            Pair pair = currentPrice.pair();
            Decimal stop = highValue.add(pair.priceDifferenceForNProfitInCounterCurrency(new Decimal("50"), size));
            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(PositionBehaviour.TRAILING)
                    .withOpenOrder(orderBuilder().withDirection(Direction.SELL).asMarketOrder().withPair(currentPrice.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(middleValue))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stop)));
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }
}
