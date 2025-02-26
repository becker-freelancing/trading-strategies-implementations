package com.becker.freelance.strategies.regression.shared;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.Direction;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.EuroDistanceEntrySignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;

import java.util.List;
import java.util.Optional;

public class PredictionToEntrySignalConverter {

    private final Decimal stopInEuro;
    private final Decimal limitInEuro;
    private final Decimal size;
    private final PositionType positionType;
    private Decimal trailingStepSize;

    public PredictionToEntrySignalConverter(Decimal stopInEuro, Decimal limitInEuro, Decimal size, PositionType positionType, Decimal trailingStepSizeInEuro) {
        this.stopInEuro = stopInEuro;
        this.limitInEuro = limitInEuro;
        this.size = size;
        this.positionType = positionType;
        this.trailingStepSize = trailingStepSizeInEuro;
    }

    public PredictionToEntrySignalConverter(Decimal stopInEuro, Decimal limitInEuro, Decimal size) {
        this(stopInEuro, limitInEuro, size, PositionType.HARD_LIMIT, Decimal.ZERO);
    }

    public Optional<EntrySignal> toEntrySignal(List<Decimal> predictions, Pair pair, TimeSeriesEntry currentPrice) {
        Decimal stopDiff = pair.priceDifferenceForNProfitInCounterCurrency(stopInEuro, size);
        Decimal limitDiff = pair.priceDifferenceForNProfitInCounterCurrency(limitInEuro, size);
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
        return switch (positionType) {
            case HARD_LIMIT ->
                    Optional.of(new EuroDistanceEntrySignal(size, Direction.SELL, stopInEuro, limitInEuro, PositionType.HARD_LIMIT));
            case TRAILING ->
                    Optional.of(new EuroDistanceEntrySignal(size, Direction.SELL, stopInEuro, limitInEuro, PositionType.TRAILING, trailingStepSize));
        };
    }

    private Optional<EntrySignal> toBuyEntrySignal(int buyLimitIdx, int buyStopIdx) {
        if (buyStopIdx <= buyLimitIdx) {
            return Optional.empty();
        }

        return switch (positionType) {
            case HARD_LIMIT ->
                    Optional.of(new EuroDistanceEntrySignal(size, Direction.BUY, stopInEuro, limitInEuro, PositionType.HARD_LIMIT));
            case TRAILING ->
                    Optional.of(new EuroDistanceEntrySignal(size, Direction.BUY, stopInEuro, limitInEuro, PositionType.TRAILING, trailingStepSize));
        };
    }
}
