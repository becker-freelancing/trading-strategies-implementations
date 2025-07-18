package com.becker.freelance.strategies.classification;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
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

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class ClassificationLiveStrategy extends BaseStrategy {

    private static final Logger logger = LoggerFactory.getLogger(ClassificationLiveStrategy.class);

    private final Double minProbabilityForEntry;
    private final Double takeProfitDelta;
    private final Double stopLossDelta;
    private final PositionBehaviour positionBehaviour;
    private final ClassificationPredictor classificationPredictor;
    private final Map<String, CachedIndicator<Num>> predictionIndicators;

    public ClassificationLiveStrategy(StrategyParameter strategyParameter, Double minProbabilityForEntry, Double takeProfitDelta, Double stopLossDelta, PositionBehaviour positionBehaviour, ClassificationPredictor classificationPredictor) {
        super(strategyParameter);
        this.minProbabilityForEntry = minProbabilityForEntry;
        this.takeProfitDelta = takeProfitDelta;
        this.stopLossDelta = stopLossDelta;
        this.positionBehaviour = positionBehaviour;
        this.classificationPredictor = classificationPredictor;

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
                        entry -> new CachedIndicator<>(classificationPredictor.getMaxRequiredInputLength(), entry.getValue())));
    }

    @Override
    protected Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {
        PredictionParameter predictionParameter = null;
        if (classificationPredictor.requiresPredictionParameter()) {
            predictionParameter = buildPredictionParameter();
        }
        Optional<ClassificationPrediction> prediction = classificationPredictor.predict(entryParameter, predictionParameter);
        logger.debug("Prediction: {}", prediction);
        return prediction.flatMap(pred -> toEntrySignal(pred, entryParameter.currentPrice()));
    }

    private PredictionParameter buildPredictionParameter() {
        QuantileMarketRegime marketRegime = currentMarketRegime();
        int inputLength = classificationPredictor.requiredInputLengthForRegime(marketRegime);
        return new DefaultPredictionParameter(
                marketRegime,
                predictionIndicators.entrySet().stream()
                        .collect(Collectors.toMap(
                                Map.Entry::getKey,
                                entry -> entry.getValue().getLastNValues(inputLength).map(Num::doubleValue).toList()))
        );
    }

    @Override
    public int unstableBars() {
        return Arrays.stream(QuantileMarketRegime.values())
                .map(classificationPredictor::requiredInputLengthForRegime)
                .mapToInt(Integer::intValue)
                .max().orElse(0);
    }

    private Optional<EntrySignalBuilder> toEntrySignal(ClassificationPrediction classificationPrediction, TimeSeriesEntry currentPrice) {
        if (classificationPrediction.maxProbabilityForBuyAndSell() > minProbabilityForEntry) {
            logger.debug("Could generate Entry Signal");
            if (classificationPrediction.buyProbability() > minProbabilityForEntry) {
                logger.debug("Generate Buy Entry Signal");
                Direction direction = Direction.BUY;
                Decimal price = currentPrice.getClosePriceForDirection(direction);
                return Optional.of(entrySignalBuilder()
                        .withPositionBehaviour(positionBehaviour)
                        .withOpenMarketRegime(currentMarketRegime())
                        .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(direction))
                        .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(price.subtract(stopLossDelta)))
                        .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(price.add(takeProfitDelta))));
            } else if (classificationPrediction.sellProbability() > minProbabilityForEntry) {
                logger.debug("Generate Sell Entry Signal");
                Direction direction = Direction.SELL;
                Decimal price = currentPrice.getClosePriceForDirection(direction);
                return Optional.of(entrySignalBuilder()
                        .withPositionBehaviour(positionBehaviour)
                        .withOpenMarketRegime(currentMarketRegime())
                        .withOpenOrder(orderBuilder().asMarketOrder().withPair(currentPrice.pair()).withDirection(direction))
                        .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(price.add(stopLossDelta)))
                        .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(price.subtract(takeProfitDelta))));

            }
        }

        return Optional.empty();
    }

    @Override
    protected Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }
}
