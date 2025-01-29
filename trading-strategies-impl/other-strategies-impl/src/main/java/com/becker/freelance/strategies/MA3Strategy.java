package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.Direction;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.math.Decimal;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;

public class MA3Strategy extends BaseStrategy {

    private static boolean validateParameter(Map<String, Decimal> parameters) {
        return parameters.get("short_period").isLessThan(parameters.get("mid_period")) &&
                parameters.get("mid_period").isLessThan(parameters.get("long_period"));
    }

    public MA3Strategy() {
        super("3_Ma_Strategy", new PermutableStrategyParameter(MA3Strategy::validateParameter,
                new StrategyParameter("short_period", 5, 3, 9, 3),
                new StrategyParameter("mid_period", 20, 10, 30, 10),
                new StrategyParameter("long_period", 200, 150, 250, 50),
                new StrategyParameter("size", 0.5, 0.2, 1., 0.2),
                new StrategyParameter("min_slope", 1, 0.4, 0.8, 0.4),
                new StrategyParameter("min_slope_window", 20, 20, 40, 20),
                new StrategyParameter("stop_points", 9, 5, 15, 5),
                new StrategyParameter("limit_points", 11, 9, 20, 5)
                ));
    }

    private Decimal size;
    private Decimal stop;
    private Decimal limit;
    private BarSeries barSeries;
    private SMAIndicator shortSma;
    private SMAIndicator midSma;
    private SMAIndicator longSma;
    private Decimal minSlope;
    private int minSlopeWindow;

    public MA3Strategy(Map<String, Decimal> parameters) {
        super(parameters);
        size = parameters.get("size");
        int longPeriod = parameters.get("long_period").intValue();
        barSeries = new BaseBarSeries();
        barSeries.setMaximumBarCount(longPeriod + 5);
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        shortSma = new SMAIndicator(closePriceIndicator, parameters.get("short_period").intValue());
        midSma = new SMAIndicator(closePriceIndicator, parameters.get("mid_period").intValue());
        longSma = new SMAIndicator(closePriceIndicator, longPeriod);
        minSlope = parameters.get("min_slope");
        minSlopeWindow = parameters.get("min_slope_window").intValue();
        stop = parameters.get("stop_points");
        limit = parameters.get("limit_points");
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Bar currentBar = timeSeries.getEntryForTimeAsBar(time);
        barSeries.addBar(currentBar);

        Optional<Direction> trendDirection = getTrendDirection();
        if (trendDirection.isEmpty()){
            return Optional.empty();
        }

        int barCount = barSeries.getBarCount();
        double currentShortSma = shortSma.getValue(barCount - 1).doubleValue();
        double lastShortSmaValue = shortSma.getValue(barCount - 2).doubleValue();
        double currentMidSma = midSma.getValue(barCount - 1).doubleValue();
        double lastMidSmaValue = midSma.getValue(barCount - 2).doubleValue();

        Direction direction = trendDirection.get();

        if (currentShortSma > currentMidSma && lastShortSmaValue < lastMidSmaValue && Direction.BUY.equals(direction)){
            return Optional.of(new EntrySignal(size, Direction.BUY, stop, limit, PositionType.HARD_LIMIT));
        } else if (currentShortSma < currentMidSma && lastShortSmaValue > lastMidSmaValue && Direction.SELL.equals(direction)){
            return Optional.of(new EntrySignal(size, Direction.SELL, stop, limit, PositionType.HARD_LIMIT));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new MA3Strategy(parameters);
    }

    private Optional<Direction> getTrendDirection() {
        int barCount = barSeries.getBarCount();
        if (barCount < minSlopeWindow){
            return Optional.empty();
        }

        double current = longSma.getValue(barCount - 1).doubleValue();
        double last = longSma.getValue(barCount - minSlopeWindow - 1).doubleValue();

        double slope = (current - last) / minSlopeWindow;
        if (minSlope.negate().isGreaterThanOrEqualTo(slope)){
            return Optional.of(Direction.SELL);
        } else if (minSlope.isLessThanOrEqualTo(slope)){
            return Optional.of(Direction.BUY);
        }
        return Optional.empty();
    }


}
