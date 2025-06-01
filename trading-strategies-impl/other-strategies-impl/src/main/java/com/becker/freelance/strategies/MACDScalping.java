package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;
import org.ta4j.core.indicators.EMAIndicator;
import org.ta4j.core.indicators.MACDIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.util.Optional;

public class MACDScalping extends BaseStrategy {

    private final MACDIndicator macdIndicator;
    private final EMAIndicator macdSignal;
    private final Decimal stopInEuros;
    private final Decimal limitInEuros;
    private final Decimal size;
    private final int longBarCount;

    public MACDScalping(StrategyCreator strategyCreator, Pair pair, int longBarCount, int shortBarCount, int signalLinePeriod, Decimal stop, Decimal limit, Decimal size) {
        super(strategyCreator, pair);

        barSeries.setMaximumBarCount(longBarCount + 3);
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        macdIndicator = new MACDIndicator(closePriceIndicator, shortBarCount, longBarCount);
        macdSignal = new EMAIndicator(macdIndicator, signalLinePeriod);
        stopInEuros = stop;
        limitInEuros = limit;
        this.size = size;
        this.longBarCount = longBarCount;
    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {

        int barCount = barSeries.getBarCount();
        if (barCount < longBarCount) {
            return Optional.empty();
        }
        double currentMacd = macdIndicator.getValue(barCount - 1).doubleValue();
        double lastMacd = macdIndicator.getValue(barCount - 2).doubleValue();
        double currentSignal = macdSignal.getValue(barCount - 1).doubleValue();
        double lastSignal = macdSignal.getValue(barCount - 2).doubleValue();

        if (currentMacd > currentSignal && lastMacd < lastSignal) {
            //BUY
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.BUY, stopInEuros, limitInEuros, PositionType.HARD_LIMIT, entryParameter.currentPrice()));
        } else if (currentMacd < currentSignal && lastMacd > lastSignal) {
            //SELL
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.SELL, stopInEuros, limitInEuros, PositionType.HARD_LIMIT, entryParameter.currentPrice()));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

}
