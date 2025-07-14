package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.regime.TradeableQuantilMarketRegime;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.indicators.ta.barseries.LogReturnBarSeries;
import com.becker.freelance.indicators.ta.cache.CachedIndicator;
import com.becker.freelance.indicators.ta.regime.MarketRegime;
import com.becker.freelance.indicators.ta.regime.QuantileMarketRegime;
import com.becker.freelance.indicators.ta.regime.RegimeIndicatorFactory;
import com.becker.freelance.indicators.ta.util.*;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.shared.DefaultPredictionParameter;
import com.becker.freelance.strategies.shared.PredictionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.ta4j.core.Indicator;
import org.ta4j.core.indicators.*;
import org.ta4j.core.indicators.bollinger.BollingerBandsLowerIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsMiddleIndicator;
import org.ta4j.core.indicators.bollinger.BollingerBandsUpperIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;
import org.ta4j.core.indicators.helpers.HighPriceIndicator;
import org.ta4j.core.indicators.helpers.LowPriceIndicator;
import org.ta4j.core.indicators.helpers.VolumeIndicator;
import org.ta4j.core.indicators.statistics.StandardDeviationIndicator;
import org.ta4j.core.num.DecimalNum;
import org.ta4j.core.num.Num;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class SequenceLiveRegressionStrategy extends BaseStrategy {

    private static final Logger logger = LoggerFactory.getLogger(SequenceLiveRegressionStrategy.class);

    private final RegressionPredictor predictor;
    private final Double takeProfitDelta;
    private final Double stopLossDelta;
    private final Double stopLossNotPredictedDelta;
    private final PositionBehaviour positionBehaviour;
    private final Map<String, CachedIndicator<Num>> predictionIndicators;

    public SequenceLiveRegressionStrategy(StrategyParameter parameter, RegressionPredictor predictor, Decimal takeProfitDelta, Decimal stopLossDelta, Decimal stopLossNotPredictedDelta, PositionBehaviour positionBehaviour) {
        super(parameter);
        this.predictor = predictor;
        this.takeProfitDelta = takeProfitDelta.doubleValue();
        this.stopLossDelta = stopLossDelta.doubleValue();
        this.stopLossNotPredictedDelta = stopLossNotPredictedDelta.doubleValue();
        this.positionBehaviour = positionBehaviour;

        Map<String, Indicator<Num>> predictionIndicators = new HashMap<>();
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(super.barSeries);
        LowPriceIndicator lowPriceIndicator = new LowPriceIndicator(super.barSeries);
        HighPriceIndicator highPriceIndicator = new HighPriceIndicator(super.barSeries);
        LogReturnIndicator logReturnClose = new LogReturnIndicator(closePriceIndicator);
        for (Integer momentumLag : new Integer[]{1, 2, 3, 6, 9, 12}) {
            predictionIndicators.put("logReturn_closeBid_" + momentumLag + "min", new LaggedLogReturnIndicator(closePriceIndicator, momentumLag));
            predictionIndicators.put("logReturn_lowBid_" + momentumLag + "min", new LaggedLogReturnIndicator(lowPriceIndicator, momentumLag));
            predictionIndicators.put("logReturn_highBid_" + momentumLag + "min", new LaggedLogReturnIndicator(highPriceIndicator, momentumLag));
        }

        LogReturnBarSeries logReturnBarSeries = new LogReturnBarSeries(super.barSeries);

        for (Integer atrPeriod : new Integer[]{5, 7, 10, 14, 18}) {
            predictionIndicators.put("ATR_" + atrPeriod, new ATRIndicator(logReturnBarSeries, atrPeriod));
        }

        for (Integer emaPeriod : new Integer[]{5, 10, 20, 30, 50, 200}) {
            predictionIndicators.put("EMA_" + emaPeriod, new EMAIndicator(logReturnClose, emaPeriod));
        }
        for (Integer rsiPeriod : new Integer[]{7, 14, 20}) {
            predictionIndicators.put("RSI_" + rsiPeriod, new RSIIndicator(logReturnClose, rsiPeriod) {
                @Override
                public int getUnstableBars() {
                    return rsiPeriod;
                }
            });
        }
        MACDIndicator macd = new MACDIndicator(logReturnClose, 12, 26) {
            @Override
            public int getUnstableBars() {
                return 26;
            }
        };
        predictionIndicators.put("MACD_12_26_9", macd);
        predictionIndicators.put("MACD_Signal_12_26_9", macd.getSignalLine(9));


        for (Integer bbPeriod : new Integer[]{15, 20, 25}) {
            SMAIndicator sma = new SMAIndicator(logReturnClose, bbPeriod);
            BollingerBandsMiddleIndicator middleIndicator = new BollingerBandsMiddleIndicator(sma) {
                @Override
                public int getUnstableBars() {
                    return sma.getUnstableBars();
                }
            };
            StandardDeviationIndicator deviationIndicator = new StandardDeviationIndicator(logReturnClose, bbPeriod);
            predictionIndicators.put("BB_Upper_" + bbPeriod, new BollingerBandsUpperIndicator(middleIndicator, deviationIndicator) {
                @Override
                public int getUnstableBars() {
                    return sma.getUnstableBars();
                }
            });
            predictionIndicators.put("BB_Lower_" + bbPeriod, new BollingerBandsLowerIndicator(middleIndicator, deviationIndicator) {
                @Override
                public int getUnstableBars() {
                    return sma.getUnstableBars();
                }
            });
            predictionIndicators.put("BB_Middle_" + bbPeriod, middleIndicator);
        }
        for (Integer momentumLag : new Integer[]{2, 3, 6, 9, 12}) {
            predictionIndicators.put("momentum_" + momentumLag,
                    new MomentumIndicator(predictionIndicators.get("logReturn_closeBid_" + momentumLag + "min"), predictionIndicators.get("logReturn_closeBid_1min")));
        }

        for (int i = 1; i < 7; i++) {
            predictionIndicators.put("logReturn_1m_t-" + i, new ShiftedIndicator(logReturnClose, i));
        }
        predictionIndicators.put("volume", new VolumeIndicator(barSeries, 1));
        Indicator<MarketRegime> marketRegimeIndicator = new RegimeIndicatorFactory().marketRegimeIndicatorFromConfigFile(getPair().technicalName(), closePriceIndicator);
        predictionIndicators.put("regime", new TransformerIndicator<>(marketRegimeIndicator, regime -> DecimalNum.valueOf(regime.getId())));


        this.predictionIndicators = predictionIndicators.entrySet().stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        entry -> new CachedIndicator<>(predictor.getMaxRequiredInputLength(), entry.getValue())));
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
    public int unstableBars() {
        return Math.max(super.unstableBars(), predictor.getMaxRequiredInputLength());
    }

    @Override
    protected Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {
//        if (!initiated) {
//            for (int i = 0; i < barSeries.getEndIndex(); i++) {
//                int finalI = i;
//                predictionIndicators.values().forEach(ind -> {
//                    if (finalI > ind.getUnstableBars()) {
//                        ind.getValue(finalI);
//                    }
//                });
//            }
//            initiated = true;
//        }
        if (barSeries.getEndIndex() < unstableBars()) {
            return Optional.empty();
        }
        PredictionParameter predictionParameter = null;
        if (predictor.requiresPredictionParameter()) {
            predictionParameter = buildPredictionParameter();
        }
        return predictor.predict(entryParameter, predictionParameter)
                .flatMap(prediction -> toEntry(entryParameter, prediction));
    }

    private PredictionParameter buildPredictionParameter() {
        QuantileMarketRegime marketRegime = currentMarketRegime();
        int inputLength = predictor.requiredInputLengthForRegime(marketRegime);
        return new DefaultPredictionParameter(
                marketRegime,
                predictionIndicators.entrySet().stream()
                        .collect(Collectors.toMap(
                                Map.Entry::getKey,
                                entry -> entry.getValue().getLastNValues(inputLength).map(Num::doubleValue).toList()))
        );
    }

    private Optional<EntrySignalBuilder> toEntry(EntryExecutionParameter entryParameter, RegressionPrediction prediction) {
        logger.debug("Prediction: {}", prediction);
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
