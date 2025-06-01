package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.indicators.ta.stochasticrsi.RsiResult;
import com.becker.freelance.indicators.ta.stochasticrsi.StochasticRsiIndicator;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;
import org.ta4j.core.Bar;
import org.ta4j.core.indicators.EMAIndicator;
import org.ta4j.core.indicators.supertrend.SuperTrendIndicator;
import org.ta4j.core.num.Num;

import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

public class SuperTrendStrategy extends BaseStrategy {


    private final EMAIndicator emaIndicator;
    private final StochasticRsiIndicator stochasticRsiIndicator;
    private final SuperTrendIndicator superTrendIndicator1;
    private final SuperTrendIndicator superTrendIndicator2;
    private final SuperTrendIndicator superTrendIndicator3;
    private final double maxRsiDiff;
    private final int maxRsiCrossAge;
    private final double riskRatio;
    private final Decimal size;
    private int lastRsiUpper80CrossAge;
    private int lastRsiLower20CrossAge;


    public SuperTrendStrategy(StrategyCreator strategyCreator,
                              Double maxRsiDiff,
                              int maxRsiCrossAge,
                              double riskRatio,
                              Decimal size,
                              int emaPeriod,
                              int rsiPeriod,
                              int rsiStochPeriod,
                              int rsiKPeriod,
                              int rsiDPeriod,
                              int supertrend1AtrPeriod,
                              double supertrend1Multiplier,
                              int supertrend2AtrPeriod,
                              double supertrend2Multiplier,
                              int supertrend3AtrPeriod,
                              double supertrend3Multiplier) {
        super(strategyCreator);

        this.maxRsiDiff = maxRsiDiff;
        this.maxRsiCrossAge = maxRsiCrossAge;
        this.riskRatio = riskRatio;
        this.size = size;
        emaIndicator = new EMAIndicator(closePrice, emaPeriod);
        stochasticRsiIndicator = new StochasticRsiIndicator(closePrice,
                rsiPeriod,
                rsiStochPeriod,
                rsiKPeriod,
                rsiDPeriod);
        superTrendIndicator1 = new SuperTrendIndicator(barSeries,
                supertrend1AtrPeriod,
                supertrend1Multiplier);
        superTrendIndicator2 = new SuperTrendIndicator(barSeries,
                supertrend2AtrPeriod,
                supertrend2Multiplier);
        superTrendIndicator3 = new SuperTrendIndicator(barSeries,
                supertrend3AtrPeriod,
                supertrend3Multiplier);

    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {

        int barCount = barSeries.getBarCount() - 1;
        Bar currentPrice = entryParameter.currentPriceAsBar();

        if (barCount < stochasticRsiIndicator.getUnstableBars()) {
            return Optional.empty();
        }

        RsiResult currentRsi = updateRsiCrosses(barCount);

        // Sind bereits Positionen geöffnet? -> Keine neuen mehr öffnen
        if (getOpenPositionRequestor().isPositionOpen(entryParameter.pair())) {
            return Optional.empty();
        }

        //Ist EMA über den Kerzen? -> Nur Short, sonst nur Long
        if (emaIndicator.getValue(barCount).isGreaterThan(currentPrice.getClosePrice())) {
            return lookForShortPosition(barCount, currentPrice, currentRsi, entryParameter.currentPrice());
        } else if (emaIndicator.getValue(barCount).isLessThan(currentPrice.getClosePrice())) {
            return lookForLongPosition(barCount, currentPrice, currentRsi, entryParameter.currentPrice());
        }

        return Optional.empty();
    }

    private Optional<EntrySignal> lookForLongPosition(int barCount, Bar currentPrice, RsiResult currentRsi, TimeSeriesEntry price) {
        List<Num> trendLinesBelowPrice = getTrendLinesBelowPrice(barCount, currentPrice);

        // Sind zwei Trendlinien unter dem Preis
        if (trendLinesBelowPrice.size() < 2) {
            return Optional.empty();
        }

        // War in letzter Zeit ein RSI-Cross und ist der RSI noch nicht zu weit gestiegen?
        if (lastRsiLower20CrossAge <= maxRsiCrossAge && currentRsi.isMidGreaterThan(20 + maxRsiDiff)) {
            return Optional.of(openLongPosition(trendLinesBelowPrice, currentPrice, price));
        }

        return Optional.empty();
    }

    private EntrySignal openLongPosition(List<Num> trendLinesBelowPrice, Bar currentPrice, TimeSeriesEntry price) {
        Decimal secondTrendLineBelowPrice = new Decimal(trendLinesBelowPrice.get(1).doubleValue());
        Decimal closePrice = new Decimal(currentPrice.getClosePrice().doubleValue());
        Decimal diffToCurrentPrice = closePrice.subtract(secondTrendLineBelowPrice).abs();
        Decimal limitLevel = closePrice.add(diffToCurrentPrice.multiply(new Decimal(riskRatio)));

        return entrySignalFactory.fromLevel(size, Direction.BUY, secondTrendLineBelowPrice, limitLevel, PositionType.HARD_LIMIT, price);
    }

    private List<Num> getTrendLinesBelowPrice(int barCount, Bar currentPrice) {
        return Stream.of(superTrendIndicator1, superTrendIndicator2, superTrendIndicator3)
                .map(indicator -> indicator.getValue(barCount))
                .filter(value -> value.isLessThan(currentPrice.getClosePrice()))
                .sorted(Comparator.comparing(Num::doubleValue))
                .toList();
    }

    private Optional<EntrySignal> lookForShortPosition(int barCount, Bar currentPrice, RsiResult currentRsi, TimeSeriesEntry price) {
        List<Num> trendLinesAbovePrice = getTrendLinesAbovePrice(barCount, currentPrice);

        // Sind zwei Trendlinien über dem Preis
        if (trendLinesAbovePrice.size() < 2) {
            return Optional.empty();
        }

        // War in letzter Zeit ein RSI-Cross und ist der RSI noch nicht zu weit abgesackt?
        if (lastRsiUpper80CrossAge <= maxRsiCrossAge && currentRsi.isMidGreaterThan(80 - maxRsiDiff)) {
            return Optional.of(openShortPosition(trendLinesAbovePrice, currentPrice, price));
        }

        return Optional.empty();
    }

    private EntrySignal openShortPosition(List<Num> trendLinesAbovePrice, Bar currentPrice, TimeSeriesEntry price) {
        Decimal secondTrendLineAbovePrice = new Decimal(trendLinesAbovePrice.get(1).doubleValue());
        Decimal closePrice = new Decimal(currentPrice.getClosePrice().doubleValue());
        Decimal diffToCurrentPrice = secondTrendLineAbovePrice.subtract(closePrice).abs();
        Decimal limitLevel = closePrice.subtract(diffToCurrentPrice.multiply(new Decimal(riskRatio)));

        return entrySignalFactory.fromLevel(size, Direction.SELL, secondTrendLineAbovePrice, limitLevel, PositionType.HARD_LIMIT, price);
    }

    private List<Num> getTrendLinesAbovePrice(int barCount, Bar currentPrice) {
        return Stream.of(superTrendIndicator1, superTrendIndicator2, superTrendIndicator3)
                .map(indicator -> indicator.getValue(barCount))
                .filter(value -> value.isGreaterThan(currentPrice.getClosePrice()))
                .sorted(Comparator.comparing(Num::doubleValue))
                .toList();
    }

    private RsiResult updateRsiCrosses(int barCount) {
        RsiResult currentRsi = stochasticRsiIndicator.getValue(barCount);
        RsiResult lastRsi = stochasticRsiIndicator.getValue(barCount - 1);

        lastRsiLower20CrossAge++;
        lastRsiUpper80CrossAge++;

        if (currentRsi.percentD().doubleValue() > 80) {
            if (currentRsi.isDGreaterK() && lastRsi.isKGreaterD()) {
                lastRsiUpper80CrossAge = 0;
            }
        } else if (currentRsi.percentD().doubleValue() < 20) {
            if (currentRsi.isKGreaterD() && lastRsi.isDGreaterK()) {
                lastRsiLower20CrossAge = 0;
            }
        }

        return currentRsi;
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

}
