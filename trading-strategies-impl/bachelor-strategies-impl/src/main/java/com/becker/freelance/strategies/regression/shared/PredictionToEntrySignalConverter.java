package com.becker.freelance.strategies.regression.shared;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.EntrySignalFactory;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;

import java.util.List;
import java.util.Optional;

public class PredictionToEntrySignalConverter {

    private final Decimal stopInEuro;
    private final Decimal limitInEuro;
    private final Decimal size;
    private final PositionType positionType;
    private final Decimal trailingStepSize;
    private final EntrySignalFactory entrySignalFactory;

    public PredictionToEntrySignalConverter(Decimal stopInEuro, Decimal limitInEuro, Decimal size, PositionType positionType, Decimal trailingStepSizeInEuro) {
        this.stopInEuro = stopInEuro;
        this.limitInEuro = limitInEuro;
        this.size = size;
        this.positionType = positionType;
        this.trailingStepSize = trailingStepSizeInEuro;
        this.entrySignalFactory = new EntrySignalFactory();
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

        return toEntrySignal(sellLimitIdx, sellStopIdx, buyLimitIdx, buyStopIdx, currentPrice);
    }

    private Optional<EntrySignal> toEntrySignal(int sellLimitIdx, int sellStopIdx, int buyLimitIdx, int buyStopIdx, TimeSeriesEntry currentPrice) {
        Optional<EntrySignal> entrySignal = Optional.empty();

        if (buyLimitIdx < sellLimitIdx && buyLimitIdx >= 0) {
            entrySignal = toBuyEntrySignal(buyLimitIdx, buyStopIdx, currentPrice);
        }

        if (sellLimitIdx >= 0 && entrySignal.isEmpty()) {
            entrySignal = toSellEntrySignal(sellLimitIdx, sellStopIdx, currentPrice);
        }

        return entrySignal;
    }

    protected Optional<EntrySignal> toSellEntrySignal(int sellLimitIdx, int sellStopIdx, TimeSeriesEntry currentPrice) {
        if (sellStopIdx <= sellLimitIdx) {
            return Optional.empty();
        }
        return switch (positionType) {
            case HARD_LIMIT ->
                    Optional.of(entrySignalFactory.fromAmount(size, Direction.SELL, stopInEuro, limitInEuro, PositionType.HARD_LIMIT, currentPrice));
            case TRAILING ->
                    Optional.of(entrySignalFactory.fromAmount(size, Direction.SELL, stopInEuro, limitInEuro, PositionType.TRAILING, currentPrice));
        };
    }

    private Optional<EntrySignal> toBuyEntrySignal(int buyLimitIdx, int buyStopIdx, TimeSeriesEntry currentPrice) {
        if (buyStopIdx <= buyLimitIdx) {
            return Optional.empty();
        }

        return switch (positionType) {
            case HARD_LIMIT ->
                    Optional.of(entrySignalFactory.fromAmount(size, Direction.BUY, stopInEuro, limitInEuro, PositionType.HARD_LIMIT, currentPrice));
            case TRAILING ->
                    Optional.of(entrySignalFactory.fromAmount(size, Direction.BUY, stopInEuro, limitInEuro, PositionType.TRAILING, currentPrice));
        };
    }
}
