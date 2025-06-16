package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
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
    protected Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {
        return predictor.predict(entryParameter, null)
                .flatMap(prediction -> toEntry(entryParameter, prediction));
    }

    @Override
    public int unstableBars() {
        return Math.max(super.unstableBars(), predictor.getMaxRequiredInputLength());
    }

    private Optional<EntrySignalBuilder> toEntry(EntryExecutionParameter entryParameter, RegressionPrediction prediction) {
        TimeSeriesEntry currentPrice = entryParameter.currentPrice();
        Double[] predictedPrice = prediction.transformLogReturnsToPrice(currentPrice);
        Double[] predictedPriceAroundZero = transformAroundZero(predictedPrice, currentPrice.getCloseMid().doubleValue());
        SignificantPoint highAroundZero = findHigh(predictedPriceAroundZero);
        SignificantPoint lowAroundZero = findLow(predictedPriceAroundZero);

        // Falls der |Hoch| > |Low| kann man durch eine Long-Position mehr gewinn machen
        if (highAroundZero.absValue() > lowAroundZero.absValue()) {
            return Optional.ofNullable(toBuyEntry(highAroundZero, lowAroundZero, predictedPrice, currentPrice, prediction.regime()));
        } else if (highAroundZero.absValue() < lowAroundZero.absValue()) {
            // Falls der |Low| > |High| kann man durch eine Long-Position mehr gewinn machen
            return Optional.ofNullable(toSellEntry(highAroundZero, lowAroundZero, predictedPrice, currentPrice, prediction.regime()));
        }

        return Optional.empty();
    }

    private EntrySignalBuilder toSellEntry(SignificantPoint highAroundZero, SignificantPoint lowAroundZero, Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        if (highAroundZero.index() < lowAroundZero.index()) {
            return toSellEntryHighBeforeLow(predictedPrice, currentPrice, marketRegime);
        } else {
            return toSellEntryLowBeforeHigh(lowAroundZero, predictedPrice, currentPrice, marketRegime);
        }
    }

    private EntrySignalBuilder toSellEntryLowBeforeHigh(SignificantPoint lowAroundZero, Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        // Falls das Tiefste Tief in der Vorhersage vor den Höchsten Hoch war muss das SL auf das höchste Hoch vor den tiefsten Tief gesetzt werden
        Double stopLevel = findHighInRange(predictedPrice, lowAroundZero.index()).value();
        Decimal limitLevel = Decimal.valueOf(findLow(predictedPrice).value() + takeProfitDelta);
        stopLevel = transformSellStopLevel(currentPrice, stopLevel);
        Decimal stopOrderPrice = Decimal.valueOf(stopLevel);
        return entrySignalBuilder()
                .withPositionBehaviour(positionBehaviour)
                .withOpenMarketRegime(marketRegime)
                .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(Direction.SELL))
                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopOrderPrice))
                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitLevel));
    }

    private EntrySignalBuilder toSellEntryHighBeforeLow(Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        // Falls das höchste Hoch vor dem tiefsten Tief kam kann man einfach bei dem höchsten Hoch das SL setzen
        Double stopLevel = findHigh(predictedPrice).value();
        stopLevel = transformSellStopLevel(currentPrice, stopLevel);
        Decimal limitLevel = Decimal.valueOf(findLow(predictedPrice).value() + takeProfitDelta);

        Decimal stopOrderPrice = Decimal.valueOf(stopLevel);
        return entrySignalBuilder()
                .withPositionBehaviour(positionBehaviour)
                .withOpenMarketRegime(marketRegime)
                .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(Direction.SELL))
                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopOrderPrice))
                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitLevel));
    }

    private Double transformSellStopLevel(TimeSeriesEntry currentPrice, Double stopLevel) {
        double closeMid = currentPrice.getCloseMid().doubleValue();
        // Falls SL unter dem aktuellen Kurs liegt (z.B. weil Vorhersage nur nach unten ging bis zum tiefsten tief) wird es um ein Delta über dem aktuellen Kurs gesetzt
        if (stopLevel < closeMid) {
            stopLevel = closeMid + stopLossNotPredictedDelta;
        }
        // Falls das SL + ein bestimmtes Delta nicht über dem aktuellen Kurs liegt wird es verschoben
        if (stopLevel + stopLossDelta > closeMid) {
            stopLevel = stopLevel + stopLossDelta;
        }
        return stopLevel;
    }

    private EntrySignalBuilder toBuyEntry(SignificantPoint highAroundZero, SignificantPoint lowAroundZero, Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        if (highAroundZero.index() < lowAroundZero.index()) {
            return toBuyEntryHighBeforeLow(highAroundZero, predictedPrice, currentPrice, marketRegime);
        } else {
            return toBuyEntryLowBeforeHigh(predictedPrice, currentPrice, marketRegime);
        }
    }

    private EntrySignalBuilder toBuyEntryLowBeforeHigh(Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Double stopLevel = findLow(predictedPrice).value();
        stopLevel = transformBuyStopLevel(currentPrice, stopLevel);
        Decimal limitLevel = Decimal.valueOf(findHigh(predictedPrice).value() - takeProfitDelta);

        Decimal stopOrderPrice = Decimal.valueOf(stopLevel);
        return entrySignalBuilder()
                .withPositionBehaviour(positionBehaviour)
                .withOpenMarketRegime(marketRegime)
                .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(Direction.BUY))
                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopOrderPrice))
                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitLevel));
    }

    private EntrySignalBuilder toBuyEntryHighBeforeLow(SignificantPoint highAroundZero, Double[] predictedPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime marketRegime) {
        Double stopLevel = findLowInRange(predictedPrice, highAroundZero.index()).value();
        stopLevel = transformBuyStopLevel(currentPrice, stopLevel);
        Decimal limitLevel = Decimal.valueOf(findHigh(predictedPrice).value() - takeProfitDelta);

        Decimal stopOrderPrice = Decimal.valueOf(stopLevel);
        return entrySignalBuilder()
                .withPositionBehaviour(positionBehaviour)
                .withOpenMarketRegime(marketRegime)
                .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(Direction.BUY))
                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(stopOrderPrice))
                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limitLevel));
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
