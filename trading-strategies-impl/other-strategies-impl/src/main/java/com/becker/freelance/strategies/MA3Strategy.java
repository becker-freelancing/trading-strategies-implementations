package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.init.PermutableStrategyInitParameter;
import com.becker.freelance.strategies.init.StrategyInitParameter;
import com.becker.freelance.strategies.parameter.EntryParameter;
import com.becker.freelance.strategies.parameter.ExitParameter;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.SMAIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.util.Map;
import java.util.Optional;

public class MA3Strategy extends BaseStrategy {

    private static boolean validateParameter(Map<String, Decimal> parameters) {
        return parameters.get("short_period").isLessThan(parameters.get("mid_period")) &&
                parameters.get("mid_period").isLessThan(parameters.get("long_period"));
    }

    public MA3Strategy() {
        super("3_Ma_Strategy", new PermutableStrategyInitParameter(MA3Strategy::validateParameter,
                new StrategyInitParameter("short_period", 5, 3, 9, 3),
                new StrategyInitParameter("mid_period", 20, 10, 30, 10),
                new StrategyInitParameter("long_period", 200, 150, 250, 50),
                new StrategyInitParameter("size", 0.5, 0.2, 1., 0.2),
                new StrategyInitParameter("min_slope", 1, 0.4, 0.8, 0.4),
                new StrategyInitParameter("min_slope_window", 20, 20, 40, 20),
                new StrategyInitParameter("stop_in_euros", 90, 50, 150, 50),
                new StrategyInitParameter("limit_in_euros", 110, 90, 200, 50)
                ));
    }

    private Decimal size;
    private Decimal stopInEuros;
    private Decimal limitInEuros;
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
        stopInEuros = parameters.get("stop_in_euros");
        limitInEuros = parameters.get("limit_in_euros");
    }

    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {
        Bar currentBar = entryParameter.currentPriceAsBar();
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
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.BUY, stopInEuros, limitInEuros, PositionType.HARD_LIMIT, entryParameter.currentPrice()));
        } else if (currentShortSma < currentMidSma && lastShortSmaValue > lastMidSmaValue && Direction.SELL.equals(direction)){
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.SELL, stopInEuros, limitInEuros, PositionType.HARD_LIMIT, entryParameter.currentPrice()));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(ExitParameter exitParameter) {
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
