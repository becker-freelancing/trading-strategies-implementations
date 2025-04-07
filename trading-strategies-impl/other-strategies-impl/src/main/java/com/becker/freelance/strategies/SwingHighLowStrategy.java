package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.indicators.ta.swing.SwingHighIndicator;
import com.becker.freelance.indicators.ta.swing.SwingHighPoint;
import com.becker.freelance.indicators.ta.swing.SwingLowIndicator;
import com.becker.freelance.indicators.ta.swing.SwingLowPoint;
import com.becker.freelance.math.Decimal;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.Indicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class SwingHighLowStrategy extends BaseStrategy {


    private BarSeries barSeries;
    private Indicator<Optional<SwingHighPoint>> swingHighIndicator;
    private Indicator<Optional<SwingLowPoint>> swingLowIndicator;
    private SwingHighPoint lastSwingHighOrNull;
    private SwingLowPoint lastSwingLowOrNull;
    private int index;
    public SwingHighLowStrategy() {
        super("swing_high_low", new PermutableStrategyParameter(List.of(
                new StrategyParameter("swing_period", 2, 2, 10, 1)
        )));

    }

    public SwingHighLowStrategy(Map<String, Decimal> parameters) {
        super(parameters);

        barSeries = new BaseBarSeries();
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        int swingPeriod = parameters.get("swing_period").intValue();
        swingHighIndicator = new SwingHighIndicator(swingPeriod, closePriceIndicator);
        swingLowIndicator = new SwingLowIndicator(swingPeriod, closePriceIndicator);
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new SwingHighLowStrategy(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {

        if (lastSwingLowOrNull == null || lastSwingHighOrNull == null) {
            return Optional.empty();
        }

        if (lastSwingHighOrNull.index() == index - 1) {
            return Optional.of(entrySignalFactory.fromAmount(new Decimal("1"), Direction.SELL, new Decimal(20), new Decimal(15), PositionType.HARD_LIMIT, timeSeries.getEntryForTime(time)));
        } else if (lastSwingLowOrNull.index() == index - 1) {
            return Optional.of(entrySignalFactory.fromAmount(new Decimal("1"), Direction.BUY, new Decimal(20), new Decimal(15), PositionType.HARD_LIMIT, timeSeries.getEntryForTime(time)));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        updateData(timeSeries, time);

        if (lastSwingLowOrNull == null || lastSwingHighOrNull == null) {
            return Optional.empty();
        }

        if (lastSwingHighOrNull.index() == index - 1) {
            return Optional.of(new ExitSignal(Direction.BUY));
        } else if (lastSwingLowOrNull.index() == index - 1) {
            return Optional.of(new ExitSignal(Direction.SELL));
        }

        return Optional.empty();
    }

    private void updateData(TimeSeries timeSeries, LocalDateTime time) {
        Bar currentPrice = timeSeries.getEntryForTimeAsBar(time);
        barSeries.addBar(currentPrice);
        index = barSeries.getBarCount() - 1;

        Optional<SwingLowPoint> optionalSwingLowPoint = swingLowIndicator.getValue(index);
        Optional<SwingHighPoint> optionalSwingHighPoint = swingHighIndicator.getValue(index);

        lastSwingHighOrNull = optionalSwingHighPoint.orElse(null);
        lastSwingLowOrNull = optionalSwingLowPoint.orElse(null);
    }
}
