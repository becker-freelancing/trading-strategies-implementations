package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;
import com.becker.freelance.strategies.regression.sequence.shared.RegressionPrediction;
import com.becker.freelance.strategies.regression.sequence.shared.RegressionPredictor;

import java.util.Optional;

public class SequenceRegressionStrategy extends BaseStrategy {

    private final RegressionPredictor predictor;
    private final Decimal size;
    private final Decimal takeProfitDelta;
    private final Decimal stopLossDelta;
    private final Decimal stopLossNotPredictedDelta;
    private final PositionType positionType;

    public SequenceRegressionStrategy(StrategyCreator strategyCreator, Pair pair, RegressionPredictor predictor, Decimal size, Decimal takeProfitDelta, Decimal stopLossDelta, Decimal stopLossNotPredictedDelta, PositionType positionType) {
        super(strategyCreator, pair);
        this.predictor = predictor;
        this.size = size;
        this.takeProfitDelta = takeProfitDelta;
        this.stopLossDelta = stopLossDelta;
        this.stopLossNotPredictedDelta = stopLossNotPredictedDelta;
        this.positionType = positionType;
    }

    private static SignificantPoint findHighInRange(Decimal[] cumsumPrediction, int maxIdx) {
        Decimal max = cumsumPrediction[0];
        int index = 0;
        for (int i = 1; i < maxIdx; i++) {
            if (cumsumPrediction[i].compareTo(max) > 0) {
                max = cumsumPrediction[i];
                index = i;
            }
        }
        return new SignificantPoint(index, max);
    }

    @Override
    protected Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {
        return predictor.predict(entryParameter)
                .flatMap(prediction -> toEntry(entryParameter, prediction));
    }

    private Optional<EntrySignal> toEntry(EntryParameter entryParameter, RegressionPrediction prediction) {
        TimeSeriesEntry currentPrice = entryParameter.currentPrice();
        Decimal[] predictedPrice = prediction.transformLogReturnsToPrice(currentPrice);
        Decimal[] predictedPriceAroundZero = transformAroundZero(predictedPrice, currentPrice.getCloseMid());
        SignificantPoint highAroundZero = findHigh(predictedPriceAroundZero);
        SignificantPoint lowAroundZero = findLow(predictedPriceAroundZero);

        if (highAroundZero.absValue().isGreaterThan(lowAroundZero.absValue())) {
            return Optional.ofNullable(toBuyEntry(highAroundZero, lowAroundZero, predictedPrice, currentPrice, prediction.regime()));
        } else if (highAroundZero.absValue().isLessThan(lowAroundZero.absValue())) {
            return Optional.ofNullable(toSellEntry(highAroundZero, lowAroundZero, predictedPrice, currentPrice, prediction.regime()));
        }

        return Optional.empty();
    }

    private EntrySignal toSellEntry(SignificantPoint highAroundZero, SignificantPoint lowAroundZero, Decimal[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        if (highAroundZero.index() < lowAroundZero.index()) {
            return toSellEntryHighBeforeLow(predictedPrice, currentPrice, marketRegime);
        } else {
            return toSellEntryLowBeforeHigh(lowAroundZero, predictedPrice, currentPrice, marketRegime);
        }
    }

    private EntrySignal toSellEntryLowBeforeHigh(SignificantPoint lowAroundZero, Decimal[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Decimal high = findHighInRange(predictedPrice, lowAroundZero.index()).value();
        if (high.isLessThan(currentPrice.getCloseMid())) {
            high = currentPrice.getCloseMid().add(stopLossNotPredictedDelta);
        }
        return entrySignalFactory.fromLevel(size, Direction.SELL,
                high.add(stopLossDelta), findLow(predictedPrice).value().add(takeProfitDelta),
                positionType, currentPrice, marketRegime);
    }

    private EntrySignal toSellEntryHighBeforeLow(Decimal[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Decimal high = findHigh(predictedPrice).value();
        if (high.isLessThan(currentPrice.getCloseMid())) {
            high = currentPrice.getCloseMid().add(stopLossNotPredictedDelta);
        }
        return entrySignalFactory.fromLevel(size, Direction.SELL,
                high.add(stopLossDelta), findLow(predictedPrice).value().add(takeProfitDelta),
                positionType, currentPrice, marketRegime);
    }

    private EntrySignal toBuyEntry(SignificantPoint highAroundZero, SignificantPoint lowAroundZero, Decimal[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        if (highAroundZero.index() < lowAroundZero.index()) {
            return toBuyEntryHighBeforeLow(highAroundZero, predictedPrice, currentPrice, marketRegime);
        } else {
            return toBuyEntryLowBeforeHigh(predictedPrice, currentPrice, marketRegime);
        }
    }

    private EntrySignal toBuyEntryLowBeforeHigh(Decimal[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Decimal low = findLow(predictedPrice).value();
        if (low.isGreaterThan(currentPrice.getCloseMid())) {
            low = currentPrice.getCloseMid().subtract(stopLossNotPredictedDelta);
        }
        return entrySignalFactory.fromLevel(size, Direction.BUY,
                low.subtract(stopLossDelta), findHigh(predictedPrice).value().subtract(takeProfitDelta),
                positionType, currentPrice, marketRegime);
    }

    private EntrySignal toBuyEntryHighBeforeLow(SignificantPoint highAroundZero, Decimal[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Decimal low = findLowInRange(predictedPrice, highAroundZero.index()).value();
        if (low.isGreaterThan(currentPrice.getCloseMid())) {
            low = currentPrice.getCloseMid().subtract(stopLossNotPredictedDelta);
        }
        return entrySignalFactory.fromLevel(size, Direction.BUY,
                low.subtract(stopLossDelta), findHigh(predictedPrice).value().subtract(takeProfitDelta),
                positionType, currentPrice, marketRegime);
    }

    private Decimal[] transformAroundZero(Decimal[] predictedPrice, Decimal currentPrice) {
        Decimal[] transformed = new Decimal[predictedPrice.length];
        for (int i = 0; i < predictedPrice.length; i++) {
            transformed[i] = predictedPrice[i].subtract(currentPrice);
        }
        return transformed;
    }

    private SignificantPoint findLow(Decimal[] cumsumPrediction) {
        return findLowInRange(cumsumPrediction, cumsumPrediction.length);
    }

    private SignificantPoint findLowInRange(Decimal[] cumsumPrediction, int maxIdx) {
        Decimal min = cumsumPrediction[0];
        int index = 0;
        for (int i = 1; i < maxIdx; i++) {
            if (cumsumPrediction[i].compareTo(min) < 0) {
                min = cumsumPrediction[i];
                index = i;
            }
        }
        return new SignificantPoint(index, min);
    }

    private SignificantPoint findHigh(Decimal[] cumsumPrediction) {
        return findHighInRange(cumsumPrediction, cumsumPrediction.length);
    }

    @Override
    protected Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

    private static record SignificantPoint(int index, Decimal value) {

        public Decimal absValue() {
            return value.abs();
        }
    }
}
