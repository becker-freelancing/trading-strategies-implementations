package com.becker.freelance.strategies;

import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.indicators.ta.swing.SwingHighIndicator;
import com.becker.freelance.indicators.ta.swing.SwingHighPoint;
import com.becker.freelance.indicators.ta.swing.SwingLowIndicator;
import com.becker.freelance.indicators.ta.swing.SwingLowPoint;
import com.becker.freelance.math.Decimal;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;
import org.ta4j.core.indicators.helpers.HighPriceIndicator;
import org.ta4j.core.indicators.helpers.LowPriceIndicator;

import java.util.List;
import java.util.Map;
import java.util.Optional;

public class SwingHighLowTest extends BaseStrategy {

    private BarSeries barSeries;
    private SwingHighIndicator swingHighIndicator;
    private SwingLowIndicator swingHighLowIndicator;
    private int period;
    public SwingHighLowTest() {
        super("Swing_High_Low_Test", new PermutableStrategyParameter(List.of(
                new StrategyParameter("period", 5, 5, 5, 1)
        )));

    }
    public SwingHighLowTest(Map<String, Decimal> parameters) {
        super(parameters);

        barSeries = new BaseBarSeries();
        period = 300;
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        HighPriceIndicator highPriceIndicator = new HighPriceIndicator(barSeries);
        LowPriceIndicator lowPriceIndicator = new LowPriceIndicator(barSeries);
        swingHighIndicator = new SwingHighIndicator(period, highPriceIndicator);
        swingHighLowIndicator = new SwingLowIndicator(period, lowPriceIndicator);
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new SwingHighLowTest(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {
        Bar currentPrice = entryParameter.currentPriceAsBar();
        barSeries.addBar(currentPrice);
        int barCount = barSeries.getBarCount();

        if (barCount < period) {
            return Optional.empty();
        }

        Optional<SwingHighPoint> value = swingHighIndicator.getValue(barCount - period);
        Optional<SwingLowPoint> value1 = swingHighLowIndicator.getValue(barCount - period);

        value.ifPresent(swingHighPoint -> System.out.println("Swing High: " + swingHighPoint.index() + ", Time: " + barSeries.getBar(swingHighPoint.index()).getBeginTime() + ", Value: " + swingHighPoint.candleValue()));
        value1.ifPresent(swingHighPoint -> System.out.println("Swing Low: " + swingHighPoint.index() + ", Time: " + barSeries.getBar(swingHighPoint.index()).getBeginTime() + ", Value: " + swingHighPoint.candleValue()));

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

    private record LastTwoMaResults(Double last, Double current) {
    }
}
