package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.EntrySignalFactory;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.math.Decimal;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.Indicator;
import org.ta4j.core.indicators.candles.*;
import org.ta4j.core.num.DecimalNum;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class ChartPatternStrategy extends BaseStrategy {

    private Decimal size;
    private Decimal stop;
    private Decimal limit;
    private BarSeries barSeries;
    private List<Indicator<Boolean>> bullishIndicator;
    private List<Indicator<Boolean>> bearischIndicator;
    private EntrySignalFactory entrySignalFactory;
    public ChartPatternStrategy() {
        super("chart_pattern", new PermutableStrategyParameter(
                new StrategyParameter("size", 1),
                new StrategyParameter("stop", 20, 10, 100, 15),
                new StrategyParameter("limit", 10, 10, 100, 15),
                new StrategyParameter("bw_bull", 0.1, 0.1, 3., 0.5),
                new StrategyParameter("buw_bull", 0.1, 0.1, 3., 0.5),
                new StrategyParameter("bc_bull", 10, 2, 50, 10),
                new StrategyParameter("fac_bull", 1., 0.5, 4., 1.)
        ));
    }


    public ChartPatternStrategy(Map<String, Decimal> parameters) {
        super(parameters);

        barSeries = new BaseBarSeries();
        stop = parameters.get("stop");
        limit = parameters.get("limit");
        size = parameters.get("size");

        bullishIndicator = List.of(
                new BullishEngulfingIndicator(barSeries),
                new BullishHaramiIndicator(barSeries),
                new InvertedHammerIndicator(barSeries, parameters.get("bw_bull").doubleValue(), parameters.get("buw_bull").doubleValue()),
                new HammerIndicator(barSeries),
                new ThreeWhiteSoldiersIndicator(barSeries, parameters.get("bc_bull").intValue(), DecimalNum.valueOf(parameters.get("fac_bull").doubleValue()))
        );

        bearischIndicator = List.of(
                new BearishEngulfingIndicator(barSeries),
                new BearishHaramiIndicator(barSeries),
                new ThreeBlackCrowsIndicator(barSeries, parameters.get("bw_bull").intValue(), parameters.get("buw_bull").doubleValue()),
                new HangingManIndicator(barSeries),
                new ShootingStarIndicator(barSeries, parameters.get("bc_bull").doubleValue(), parameters.get("fac_bull").doubleValue())
        );
        entrySignalFactory = new EntrySignalFactory();
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Bar currentPrice = timeSeries.getEntryForTimeAsBar(time);
        barSeries.addBar(currentPrice);
        int index = barSeries.getBarCount() - 1;
        boolean bullish = bullishIndicator.stream().anyMatch(ind -> ind.getValue(index));
        if (bullish) {
            return Optional.of(
                    entrySignalFactory.fromDistance(size, Direction.BUY, stop, limit, PositionType.HARD_LIMIT, timeSeries.getEntryForTime(time))
            );
        }
        boolean bearish = bearischIndicator.stream().anyMatch(ind -> ind.getValue(index));
        if (bearish) {
            return Optional.of(
                    entrySignalFactory.fromDistance(size, Direction.SELL, stop, limit, PositionType.HARD_LIMIT, timeSeries.getEntryForTime(time))
            );
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new ChartPatternStrategy(parameters);
    }
}
