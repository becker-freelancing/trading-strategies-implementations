package com.becker.freelance.strategies;

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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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

    private static final Logger logger = LoggerFactory.getLogger(BollingerBandBounceStrategy.class);


    private final SMAIndicator smaIndicator;
    private final StandardDeviationIndicator standardDeviationIndicator;

    private final BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator;
    private final BollingerBandsUpperIndicator bollingerBandsUpperIndicator;
    private final BollingerBandsLowerIndicator bollingerBandsLowerIndicator;
    private final Decimal stopDistance;
    private final Decimal takeProfitDelta;
    private final PositionBehaviour positionBehaviour;

    public BollingerBandBounceStrategy(StrategyParameter parameter, int period, Decimal std, Decimal stopDistance, Decimal takeProfitDelta, PositionBehaviour positionBehaviour) {
        super(parameter);
        this.stopDistance = stopDistance;
        this.positionBehaviour = positionBehaviour;
        this.takeProfitDelta = takeProfitDelta;
        smaIndicator = new SMAIndicator(closePrice, period);
        standardDeviationIndicator = new StandardDeviationIndicator(closePrice, period);
        bollingerBandsMiddleIndicator = new BollingerBandsMiddleIndicator(smaIndicator);
        bollingerBandsUpperIndicator = new BollingerBandsUpperIndicator(bollingerBandsMiddleIndicator, standardDeviationIndicator, DecimalNum.valueOf(std));
        bollingerBandsLowerIndicator = new BollingerBandsLowerIndicator(bollingerBandsMiddleIndicator, standardDeviationIndicator, DecimalNum.valueOf(std));
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        TimeSeriesEntry currentPrice = entryParameter.currentPrice();

        Optional<EntrySignalBuilder> buyEntrySignal = toBuyEntrySignal(barSeries, bollingerBandsLowerIndicator, bollingerBandsMiddleIndicator, currentPrice);
        if (buyEntrySignal.isPresent()) {
            return buyEntrySignal;
        }

        Optional<EntrySignalBuilder> sellEntrySignal = toSellEntrySignal(barSeries, bollingerBandsUpperIndicator, bollingerBandsMiddleIndicator, currentPrice);
        return sellEntrySignal;
    }

    private Optional<EntrySignalBuilder> toBuyEntrySignal(BarSeries series, BollingerBandsLowerIndicator bollingerBandsLowerIndicator, BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator, TimeSeriesEntry currentPrice) {
        int barCount = series.getEndIndex();
        Num lowValueNum = bollingerBandsLowerIndicator.getValue(barCount);
        Decimal lowValue = new Decimal(lowValueNum.doubleValue());
        Decimal closeMid = currentPrice.getCloseMid();
        if (currentPrice.getOpenMid().isLessThan(lowValue) && closeMid.isGreaterThan(lowValue)) {
            Num middleValueNum = bollingerBandsMiddleIndicator.getValue(barCount);
            Decimal middleValue = new Decimal(middleValueNum.doubleValue());
            Decimal tpLevel = middleValue.add(takeProfitDelta);
            Decimal slLevel = stopDistanceToLevel(currentPrice, stopDistance, Direction.BUY);

            logger.debug("Creating Buy Entry Signal with TP Level {} and SL Level {}", tpLevel, slLevel);

            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(positionBehaviour)
                    .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(currentPrice.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(tpLevel))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(slLevel)));
        }
        return Optional.empty();
    }

    private Optional<EntrySignalBuilder> toSellEntrySignal(BarSeries series, BollingerBandsUpperIndicator bollingerBandsUpperIndicator, BollingerBandsMiddleIndicator bollingerBandsMiddleIndicator, TimeSeriesEntry currentPrice) {
        int barCount = series.getEndIndex();
        Decimal highValue = new Decimal(bollingerBandsUpperIndicator.getValue(barCount).doubleValue());
        Decimal closeMid = currentPrice.getCloseMid();
        if (currentPrice.getOpenMid().isGreaterThan(highValue) && closeMid.isLessThan(highValue)) {
            Decimal middleValue = new Decimal(bollingerBandsMiddleIndicator.getValue(barCount).doubleValue());
            Decimal tpLevel = middleValue.subtract(takeProfitDelta);
            Decimal slLevel = stopDistanceToLevel(currentPrice, stopDistance, Direction.SELL);
            logger.debug("Creating Sell Entry Signal with TP Level {} and SL Level {}", tpLevel, slLevel);
            return Optional.of(entrySignalBuilder()
                    .withOpenMarketRegime(currentMarketRegime())
                    .withPositionBehaviour(positionBehaviour)
                    .withOpenOrder(orderBuilder().withDirection(Direction.SELL).asMarketOrder().withPair(currentPrice.pair()))
                    .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(tpLevel))
                    .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(slLevel)));
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }
}
