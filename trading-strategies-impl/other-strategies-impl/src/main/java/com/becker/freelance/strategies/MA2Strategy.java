package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.algorithm.SwingDetection;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.util.List;
import java.util.Optional;

public class MA2Strategy extends BaseStrategy {

    private static final Logger logger = LoggerFactory.getLogger(MA2Strategy.class);


    private final int swingHighLowMaxAge;
    private final int swingHighLowOrder;
    private final SwingDetection swingDetection;
    private final SMAIndicator shortSma;
    private final SMAIndicator longSma;
    private final Decimal stopLossDelta;
    private final Decimal takeProfitDelta;
    private final PositionBehaviour positionBehaviour;

    public MA2Strategy(StrategyParameter parameter, int shortMaPeriod, int longMaPeriod, int swingHighLowMaxAge, int swingHighLowOrder, Decimal stopLossDelta, Decimal takeProfitDelta, PositionBehaviour positionBehaviour) {
        super(parameter);

        this.swingHighLowMaxAge = swingHighLowMaxAge;
        this.swingHighLowOrder = swingHighLowOrder;
        this.stopLossDelta = stopLossDelta;
        this.takeProfitDelta = takeProfitDelta;
        this.positionBehaviour = positionBehaviour;
        this.swingDetection = new SwingDetection();
        barSeries.setMaximumBarCount(Math.max(longMaPeriod, swingHighLowOrder));
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        shortSma = new SMAIndicator(closePriceIndicator, shortMaPeriod);
        longSma = new SMAIndicator(closePriceIndicator, longMaPeriod);
    }

    private LastTwoMaResults lastTwoMaValuesForTime(SMAIndicator smaIndicator, int barCount) {
        double last = smaIndicator.getValue(barCount - 1).doubleValue();
        double current = smaIndicator.getValue(barCount).doubleValue();
        return new LastTwoMaResults(last, current);
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        int barCount = barSeries.getEndIndex();
        LastTwoMaResults lastShortMaValues = lastTwoMaValuesForTime(shortSma, barCount);
        LastTwoMaResults lastLongMaValues = lastTwoMaValuesForTime(longSma, barCount);

        int swingDataCount = swingHighLowMaxAge + swingHighLowOrder;
        Optional<List<TimeSeriesEntry>> optionalSwingHighLowData = entryParameter.timeSeries().getLastNCloseForTimeAsEntryIfExist(entryParameter.time(), swingDataCount);

        logger.debug("Swing detection data is present {}", optionalSwingHighLowData.isPresent());

        if (optionalSwingHighLowData.isEmpty()) {
            return Optional.empty();
        }
        return toEntrySignal(lastShortMaValues, lastLongMaValues, optionalSwingHighLowData.get(), swingHighLowOrder, entryParameter.currentPrice());
    }

    private Optional<EntrySignalBuilder> toEntrySignal(LastTwoMaResults lastShortMaValues, LastTwoMaResults lastLongMaValues, List<TimeSeriesEntry> swingData, int swingOrder, TimeSeriesEntry current) {
        Double lastShort = lastShortMaValues.last();
        Double currentShort = lastShortMaValues.current();
        Double lastLong = lastLongMaValues.last();
        Double currentLong = lastLongMaValues.current();

        if (lastShort < lastLong && currentShort > currentLong) {
            logger.debug("Buy Position could be opened");
            //BUY
            Optional<TimeSeriesEntry> lastSwingLow = swingDetection.getLastSwingLow(swingData, swingOrder);
            lastSwingLow.ifPresentOrElse(low -> logger.debug("Last Swing low was {}", low), () -> logger.debug("No swing low detected"));
            Pair pair = current.pair();
            return lastSwingLow.map(swingValue -> swingValue.getCloseMid().subtract(stopLossDelta))
                    .map(stopLevel -> {
                        return entrySignalBuilder()
                                .withOpenMarketRegime(currentMarketRegime())
                                .withPositionBehaviour(positionBehaviour)
                                .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(current.pair()))
                                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(current.getCloseMid().add(takeProfitDelta)))
                                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopLevel));
                    });
        } else if (lastShort > lastLong && currentShort < currentLong) {
            logger.debug("Sell Position could be opened");
            //SELL
            Optional<TimeSeriesEntry> lastSwingHigh = swingDetection.getLastSwingHigh(swingData, swingOrder);
            lastSwingHigh.ifPresentOrElse(low -> logger.debug("Last Swing High was {}", low), () -> logger.debug("No swing high detected"));
            Pair pair = current.pair();
            return lastSwingHigh.map(swingValue -> swingValue.getCloseMid().add(stopLossDelta))
                    .map(stopLevel -> {

                        return entrySignalBuilder()
                                .withOpenMarketRegime(currentMarketRegime())
                                .withPositionBehaviour(positionBehaviour)
                                .withOpenOrder(orderBuilder().withDirection(Direction.SELL).asMarketOrder().withPair(current.pair()))
                                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(current.getCloseMid().subtract(takeProfitDelta)))
                                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopLevel));
                    });
        }
        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }

    private record LastTwoMaResults(Double last, Double current) {
    }
}
