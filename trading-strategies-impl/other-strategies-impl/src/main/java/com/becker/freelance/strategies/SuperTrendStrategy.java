package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.indicators.ta.stochasticrsi.RsiResult;
import com.becker.freelance.indicators.ta.stochasticrsi.StochasticRsiIndicator;
import com.becker.freelance.math.Decimal;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.EMAIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;
import org.ta4j.core.indicators.supertrend.SuperTrendIndicator;
import org.ta4j.core.num.Num;

import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Stream;

public class SuperTrendStrategy extends BaseStrategy {


    private EMAIndicator emaIndicator;
    private StochasticRsiIndicator stochasticRsiIndicator;
    private SuperTrendIndicator superTrendIndicator1;
    private SuperTrendIndicator superTrendIndicator2;
    private SuperTrendIndicator superTrendIndicator3;
    private BarSeries barSeries;
    private double maxRsiDiff;
    private int maxRsiCrossAge;
    private double riskRatio;
    private Decimal size;
    private int lastRsiUpper80CrossAge;
    private int lastRsiLower20CrossAge;
    public SuperTrendStrategy() {
        super("super_trend", new PermutableStrategyParameter(
                new StrategyParameter("rsi_k", 3),
                new StrategyParameter("rsi_d", 3),
                new StrategyParameter("rsi_length", 14, 13, 15, 1),
                new StrategyParameter("rsi_stoch_length", 14),
                new StrategyParameter("rsi_cross_max_age", 5, 5, 15, 5),
                new StrategyParameter("size", 0.2, 0.2, 1.2, 0.2),
                new StrategyParameter("risk_ratio", 1.5, 1., 2., 0.2),
                new StrategyParameter("max_rsi_diff", 20, 0, 30, 10),
                new StrategyParameter("ema_period", 200),
                new StrategyParameter("supertrend_1_atr", 10),
                new StrategyParameter("supertrend_1_multiplier", 1),
                new StrategyParameter("supertrend_2_atr", 11),
                new StrategyParameter("supertrend_2_multiplier", 2),
                new StrategyParameter("supertrend_3_atr", 12),
                new StrategyParameter("supertrend_3_multiplier", 3)
        ));
    }

    public SuperTrendStrategy(Map<String, Decimal> parameters) {
        super(parameters);

        maxRsiDiff = parameters.get("max_rsi_diff").doubleValue();
        maxRsiCrossAge = parameters.get("rsi_cross_max_age").intValue();
        riskRatio = parameters.get("risk_ratio").doubleValue();
        size = parameters.get("size");
        barSeries = new BaseBarSeries();
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        emaIndicator = new EMAIndicator(closePriceIndicator, parameters.get("ema_period").intValue());
        stochasticRsiIndicator = new StochasticRsiIndicator(closePriceIndicator,
                parameters.get("rsi_length").intValue(),
                parameters.get("rsi_stoch_length").intValue(),
                parameters.get("rsi_k").intValue(),
                parameters.get("rsi_d").intValue());
        superTrendIndicator1 = new SuperTrendIndicator(barSeries,
                parameters.get("supertrend_1_atr").intValue(),
                parameters.get("supertrend_1_multiplier").doubleValue());
        superTrendIndicator2 = new SuperTrendIndicator(barSeries,
                parameters.get("supertrend_2_atr").intValue(),
                parameters.get("supertrend_2_multiplier").doubleValue());
        superTrendIndicator3 = new SuperTrendIndicator(barSeries,
                parameters.get("supertrend_3_atr").intValue(),
                parameters.get("supertrend_3_multiplier").doubleValue());

    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Bar currentPrice = timeSeries.getEntryForTimeAsBar(time);
        barSeries.addBar(currentPrice);
        int barCount = barSeries.getBarCount() - 1;

        if (barCount < stochasticRsiIndicator.getUnstableBars()) {
            return Optional.empty();
        }

        RsiResult currentRsi = updateRsiCrosses(barCount);

        // Sind bereits Positionen geöffnet? -> Keine neuen mehr öffnen
        if (getOpenPositionRequestor().isPositionOpen(timeSeries.getPair())) {
            return Optional.empty();
        }

        //Ist EMA über den Kerzen? -> Nur Short, sonst nur Long
        if (emaIndicator.getValue(barCount).isGreaterThan(currentPrice.getClosePrice())) {
            return lookForShortPosition(barCount, currentPrice, currentRsi, timeSeries.getEntryForTime(time));
        } else if (emaIndicator.getValue(barCount).isLessThan(currentPrice.getClosePrice())) {
            return lookForLongPosition(barCount, currentPrice, currentRsi, timeSeries.getEntryForTime(time));
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
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new SuperTrendStrategy(parameters);
    }
}
