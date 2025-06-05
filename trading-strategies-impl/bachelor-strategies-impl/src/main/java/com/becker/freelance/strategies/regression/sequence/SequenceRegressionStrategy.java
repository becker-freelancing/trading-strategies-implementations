package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;

import java.util.Optional;

public class SequenceRegressionStrategy extends BaseStrategy {

    private final RegressionPredictor predictor;
    private final Double takeProfitDelta;
    private final Double stopLossDelta;
    private final Double stopLossNotPredictedDelta;
    private final PositionBehaviour positionBehaviour;

    public SequenceRegressionStrategy(StrategyParameter parameter, RegressionPredictor predictor, Decimal takeProfitDelta, Decimal stopLossDelta, Decimal stopLossNotPredictedDelta, PositionBehaviour positionBehaviour) {
        super(parameter);
        this.predictor = predictor;
        this.takeProfitDelta = takeProfitDelta.doubleValue();
        this.stopLossDelta = stopLossDelta.doubleValue();
        this.stopLossNotPredictedDelta = stopLossNotPredictedDelta.doubleValue();
        this.positionBehaviour = positionBehaviour;
    }

    private static SignificantPoint findHighInRange(Double[] cumsumPrediction, int maxIdx) {
        Double max = cumsumPrediction[0];
        int index = 0;
        for (int i = 1; i < maxIdx; i++) {
            if (cumsumPrediction[i] > max) {
                max = cumsumPrediction[i];
                index = i;
            }
        }
        return new SignificantPoint(index, max);
    }

    @Override
    protected Optional<EntrySignal> internalShouldEnter(EntryExecutionParameter entryParameter) {
        return predictor.predict(entryParameter)
                .flatMap(prediction -> toEntry(entryParameter, prediction));
    }

    private Optional<EntrySignal> toEntry(EntryExecutionParameter entryParameter, RegressionPrediction prediction) {
        TimeSeriesEntry currentPrice = entryParameter.currentPrice();
        Double[] predictedPrice = prediction.transformLogReturnsToPrice(currentPrice);
        Double[] predictedPriceAroundZero = transformAroundZero(predictedPrice, currentPrice.getCloseMid().doubleValue());
        SignificantPoint highAroundZero = findHigh(predictedPriceAroundZero);
        SignificantPoint lowAroundZero = findLow(predictedPriceAroundZero);

        if (highAroundZero.absValue() > lowAroundZero.absValue()) {
            return Optional.ofNullable(toBuyEntry(highAroundZero, lowAroundZero, predictedPrice, currentPrice, prediction.regime()));
        } else if (highAroundZero.absValue() < lowAroundZero.absValue()) {
            return Optional.ofNullable(toSellEntry(highAroundZero, lowAroundZero, predictedPrice, currentPrice, prediction.regime()));
        }

        return Optional.empty();
    }

    private EntrySignal toSellEntry(SignificantPoint highAroundZero, SignificantPoint lowAroundZero, Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        if (highAroundZero.index() < lowAroundZero.index()) {
            return toSellEntryHighBeforeLow(predictedPrice, currentPrice, marketRegime);
        } else {
            return toSellEntryLowBeforeHigh(lowAroundZero, predictedPrice, currentPrice, marketRegime);
        }
    }

    private EntrySignal toSellEntryLowBeforeHigh(SignificantPoint lowAroundZero, Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Double stopLevel = findHighInRange(predictedPrice, lowAroundZero.index()).value();
        stopLevel = transformSellStopLevel(currentPrice, stopLevel);
        return entrySignalFactory.fromLevel(Decimal.ONE, Direction.SELL,
                Decimal.valueOf(stopLevel), Decimal.valueOf(findLow(predictedPrice).value() + takeProfitDelta),
                positionBehaviour, currentPrice, marketRegime);
    }

    private EntrySignal toSellEntryHighBeforeLow(Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Double stopLevel = findHigh(predictedPrice).value();
        stopLevel = transformSellStopLevel(currentPrice, stopLevel);
        return entrySignalFactory.fromLevel(Decimal.ONE, Direction.SELL,
                Decimal.valueOf(stopLevel), Decimal.valueOf(findLow(predictedPrice).value() + takeProfitDelta),
                positionBehaviour, currentPrice, marketRegime);
    }

    private Double transformSellStopLevel(TimeSeriesEntry currentPrice, Double stopLevel) {
        double closeMid = currentPrice.getCloseMid().doubleValue();
        if (stopLevel < closeMid) {
            stopLevel = closeMid + stopLossNotPredictedDelta;
        }
        if (stopLevel + stopLossDelta > closeMid) {
            stopLevel = stopLevel + stopLossDelta;
        }
        return stopLevel;
    }

    private EntrySignal toBuyEntry(SignificantPoint highAroundZero, SignificantPoint lowAroundZero, Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        if (highAroundZero.index() < lowAroundZero.index()) {
            return toBuyEntryHighBeforeLow(highAroundZero, predictedPrice, currentPrice, marketRegime);
        } else {
            return toBuyEntryLowBeforeHigh(predictedPrice, currentPrice, marketRegime);
        }
    }

    private EntrySignal toBuyEntryLowBeforeHigh(Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Double stopLevel = findLow(predictedPrice).value();
        stopLevel = transformBuyStopLevel(currentPrice, stopLevel);
        return entrySignalFactory.fromLevel(Decimal.ONE, Direction.BUY,
                Decimal.valueOf(stopLevel), Decimal.valueOf(findHigh(predictedPrice).value() - takeProfitDelta),
                positionBehaviour, currentPrice, marketRegime);
    }

    private EntrySignal toBuyEntryHighBeforeLow(SignificantPoint highAroundZero, Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Double stopLevel = findLowInRange(predictedPrice, highAroundZero.index()).value();
        stopLevel = transformBuyStopLevel(currentPrice, stopLevel);
        return entrySignalFactory.fromLevel(Decimal.ONE, Direction.BUY,
                Decimal.valueOf(stopLevel), Decimal.valueOf(findHigh(predictedPrice).value() - takeProfitDelta),
                positionBehaviour, currentPrice, marketRegime);
    }

    private Double transformBuyStopLevel(TimeSeriesEntry currentPrice, Double stopLevel) {
        double closeMid = currentPrice.getCloseMid().doubleValue();
        if (stopLevel > closeMid) {
            stopLevel = closeMid - stopLossNotPredictedDelta;
        }
        if (stopLevel - stopLossDelta < closeMid) {
            stopLevel = stopLevel - stopLossDelta;
        }
        return stopLevel;
    }

    private Double[] transformAroundZero(Double[] predictedPrice, Double currentPrice) {
        Double[] transformed = new Double[predictedPrice.length];
        for (int i = 0; i < predictedPrice.length; i++) {
            transformed[i] = predictedPrice[i] - currentPrice;
        }
        return transformed;
    }

    private SignificantPoint findLow(Double[] cumsumPrediction) {
        return findLowInRange(cumsumPrediction, cumsumPrediction.length);
    }

    private SignificantPoint findLowInRange(Double[] cumsumPrediction, int maxIdx) {
        Double min = cumsumPrediction[0];
        int index = 0;
        for (int i = 1; i < maxIdx; i++) {
            if (cumsumPrediction[i] < min) {
                min = cumsumPrediction[i];
                index = i;
            }
        }
        return new SignificantPoint(index, min);
    }

    private SignificantPoint findHigh(Double[] cumsumPrediction) {
        return findHighInRange(cumsumPrediction, cumsumPrediction.length);
    }

    @Override
    protected Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }

    private static record SignificantPoint(int index, Double value) {

        public Double absValue() {
            return Math.abs(value);
        }
    }
}
