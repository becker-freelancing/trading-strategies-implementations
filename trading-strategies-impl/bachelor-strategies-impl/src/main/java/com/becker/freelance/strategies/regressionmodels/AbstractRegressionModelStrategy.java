package com.becker.freelance.strategies.regressionmodels;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.Direction;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.EuroDistanceEntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;
import com.becker.freelance.strategies.PermutableStrategyParameter;
import com.becker.freelance.strategies.StrategyParameter;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public abstract class AbstractRegressionModelStrategy extends BaseStrategy {

    private Decimal size;
    private Decimal limitInEuro;
    private Decimal stopInEuro;
    private BufferedPredictor predictor;

    public AbstractRegressionModelStrategy(String name) {
        super(name, new PermutableStrategyParameter(
                new StrategyParameter("size", 0.5, 0.2, 1., 0.2),
                new StrategyParameter("limit_in_euros", 150, 130, 220, 30),
                new StrategyParameter("stop_in_euros", 80, 60, 120, 20)
        ));
    }

    protected AbstractRegressionModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
        size = parameters.get("size");
        limitInEuro = parameters.get("limit_in_euros");
        stopInEuro = parameters.get("stop_in_euros");
        predictor = new BufferedPredictor(getModelName(), getModelId());
    }


    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Optional<List<Decimal>> optionalPrediction = predictor.getPrediction(time);

        if (optionalPrediction.isEmpty()) {
            return Optional.empty();
        }

        List<Decimal> prediction = optionalPrediction.get();
        return toEntrySignal(prediction, timeSeries.getPair(), timeSeries.getEntryForTime(time));
    }

    private Optional<EntrySignal> toEntrySignal(List<Decimal> predictions, Pair pair, TimeSeriesEntry currentPrice) {
        Decimal stopDiff = pair.priceDifferenceForNProfitInCounterCurrency(stopInEuro);
        Decimal limitDiff = pair.priceDifferenceForNProfitInCounterCurrency(limitInEuro);
        Decimal closeMid = currentPrice.getCloseMid();
        Decimal sellLimit = closeMid.subtract(limitDiff);
        Decimal sellStop = closeMid.add(stopDiff);
        Decimal buyLimit = closeMid.add(limitDiff);
        Decimal buyStop = closeMid.subtract(stopDiff);

        int sellLimitIdx = -1;
        int sellStopIdx = -1;
        int buyLimitIdx = -1;
        int buyStopIdx = -1;

        for (int i = 0; i < predictions.size(); i++) {
            Decimal prediction = predictions.get(i);
            if (sellLimitIdx < 0 && prediction.isLessThanOrEqualTo(sellLimit)) {
                sellLimitIdx = i;
            } else if (sellStopIdx < 0 && prediction.isGreaterThanOrEqualTo(sellStop)) {
                sellStopIdx = i;
            }

            if (buyStopIdx < 0 && prediction.isLessThanOrEqualTo(buyStop)) {
                buyStopIdx = i;
            } else if (buyLimitIdx < 0 && prediction.isGreaterThanOrEqualTo(buyLimit)) {
                buyLimitIdx = i;
            }
        }

        return toEntrySignal(sellLimitIdx, sellStopIdx, buyLimitIdx, buyStopIdx);
    }

    private Optional<EntrySignal> toEntrySignal(int sellLimitIdx, int sellStopIdx, int buyLimitIdx, int buyStopIdx) {
        Optional<EntrySignal> entrySignal = Optional.empty();

        if (buyLimitIdx < sellLimitIdx && buyLimitIdx >= 0) {
            entrySignal = toBuyEntrySignal(buyLimitIdx, buyStopIdx);
        }

        if (sellLimitIdx >= 0 && entrySignal.isEmpty()) {
            entrySignal = toSellEntrySignal(sellLimitIdx, sellStopIdx);
        }

        return entrySignal;
    }

    protected Optional<EntrySignal> toSellEntrySignal(int sellLimitIdx, int sellStopIdx) {
        if (sellStopIdx <= sellLimitIdx) {
            return Optional.empty();
        }
        return Optional.of(new EuroDistanceEntrySignal(size, Direction.SELL, stopInEuro, limitInEuro, PositionType.HARD_LIMIT));
    }

    private Optional<EntrySignal> toBuyEntrySignal(int buyLimitIdx, int buyStopIdx) {
        if (buyStopIdx <= buyLimitIdx) {
            return Optional.empty();
        }
        return Optional.of(new EuroDistanceEntrySignal(size, Direction.BUY, stopInEuro, limitInEuro, PositionType.HARD_LIMIT));
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    protected abstract String getModelName();

    protected abstract int getModelId();
}
