package com.becker.freelance.strategies;

import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.indicators.ta.supportresistence.*;
import com.becker.freelance.math.Decimal;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;
import org.ta4j.core.num.DecimalNum;

import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class SupportResistenceTest extends BaseStrategy {

    private BarSeries barSeries;
    private SupportIndicator supportIndicator;
    private ResistenceIndicator resistenceIndicator;
    private int period;

    public SupportResistenceTest() {
        super("support_resistence", new PermutableStrategyParameter(List.of(
                new StrategyParameter("period", 5, 5, 5, 1)
        )));

    }

    public SupportResistenceTest(Map<String, Decimal> parameters) {
        super(parameters);

        barSeries = new BaseBarSeries();
        period = 100;
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        supportIndicator = new SupportIndicator(DecimalNum.valueOf(0.01), period, closePriceIndicator);
        resistenceIndicator = new ResistenceIndicator(DecimalNum.valueOf(0.01), period, closePriceIndicator);
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new SupportResistenceTest(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Bar currentPrice = timeSeries.getEntryForTimeAsBar(time);
        barSeries.addBar(currentPrice);
        int barCount = barSeries.getBarCount();

        if (barCount < 8000) {
            return Optional.empty();
        }

        List<Support> supports = supportIndicator.getValue(barCount - 1);
        List<Resistence> resistences = resistenceIndicator.getValue(barCount - 1);

        supports.forEach(support -> print(barSeries, support));
        System.out.println("~~~~~~~~~~~~~~~~");
        resistences.forEach(resistence -> print(barSeries, resistence));

        throw new IllegalStateException();
//        return Optional.empty();
    }

    private void print(BarSeries barSeries, Zone<?> support) {
        System.out.println(support);
        support.hits().stream()
                .map(hit -> barSeries.getBar(hit.index()))
                .sorted(Comparator.comparing(Bar::getBeginTime))
                .forEach(bar -> {
                    System.out.println("\t\t" + bar.getBeginTime() + " - " + bar.getClosePrice());
                });
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    private record LastTwoMaResults(Double last, Double current) {
    }
}
