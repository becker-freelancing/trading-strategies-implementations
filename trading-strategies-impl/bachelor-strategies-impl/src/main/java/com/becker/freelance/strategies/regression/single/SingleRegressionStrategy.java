package com.becker.freelance.strategies.regression.single;

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


public class SingleRegressionStrategy extends BaseStrategy {

    private final SingleRegressionPredictor predictor;
    private final Double takeProfitDelta;
    private final Double stopLossDelta;
    private final Double stopLossNotPredictedDelta;
    private final PositionBehaviour positionBehaviour;

    public SingleRegressionStrategy(StrategyParameter parameter, SingleRegressionPredictor predictor, Decimal takeProfitDelta, Decimal stopLossDelta, Decimal stopLossNotPredictedDelta, PositionBehaviour positionBehaviour) {
        super(parameter);
        this.predictor = predictor;
        this.takeProfitDelta = takeProfitDelta.doubleValue();
        this.stopLossDelta = stopLossDelta.doubleValue();
        this.stopLossNotPredictedDelta = stopLossNotPredictedDelta.doubleValue();
        this.positionBehaviour = positionBehaviour;
    }

    @Override
    protected Optional<EntrySignal> internalShouldEnter(EntryExecutionParameter entryParameter) {
        return predictor.predict(entryParameter)
                .flatMap(prediction -> toEntry(entryParameter, prediction));
    }

    private Optional<EntrySignal> toEntry(EntryExecutionParameter entryParameter, SingleRegressionPrediction prediction) {
        TimeSeriesEntry currentPrice = entryParameter.currentPrice();
        Double minPrice = prediction.minInverseTransformer().transformLogReturnsToPrice(currentPrice);
        Double maxPrice = prediction.maxInverseTransformer().transformLogReturnsToPrice(currentPrice);

        Double minAbsDiffToCurrent = absDiffToCurrent(minPrice, currentPrice);
        Double maxAbsDiffToCurrent = absDiffToCurrent(maxPrice, currentPrice);

        if (maxAbsDiffToCurrent > minAbsDiffToCurrent) {
            return Optional.of(toBuyEntry(minPrice, maxPrice, currentPrice, prediction.regime()));
        }

        return Optional.of(toSellEntry(minPrice, maxPrice, currentPrice, prediction.regime()));
    }

    private EntrySignal toSellEntry(Double minPrice, Double maxPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime regime) {
        Double stopLevel = maxPrice;
        stopLevel = transformSellStopLevel(currentPrice, stopLevel);
        return entrySignalFactory.fromLevel(Decimal.ONE, Direction.SELL,
                Decimal.valueOf(stopLevel), Decimal.valueOf(minPrice + takeProfitDelta),
                positionBehaviour, currentPrice, regime);
    }

    private EntrySignal toBuyEntry(Double minPrice, Double maxPrice, TimeSeriesEntry currentPrice, TradeableQuantilMarketRegime quantileMarketRegime) {
        Double stopLevel = minPrice;
        stopLevel = transformBuyStopLevel(currentPrice, stopLevel);
        return entrySignalFactory.fromLevel(Decimal.ONE, Direction.BUY,
                Decimal.valueOf(stopLevel), Decimal.valueOf(maxPrice - takeProfitDelta),
                positionBehaviour, currentPrice, quantileMarketRegime);
    }

    private Double absDiffToCurrent(Double price, TimeSeriesEntry currentPrice) {
        return Math.abs(price - currentPrice.getCloseMid().doubleValue());
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

    @Override
    protected Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }

}
