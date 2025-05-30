package com.becker.freelance.strategies;

import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.indicators.ta.supportresistence.Zone;
import com.becker.freelance.indicators.ta.swing.SwingPoint;
import com.becker.freelance.indicators.ta.trend.TrendChanel;
import com.becker.freelance.indicators.ta.trend.TrendChanelIndicator;
import com.becker.freelance.indicators.ta.trend.TrendIndicator;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.init.PermutableStrategyInitParameter;
import com.becker.freelance.strategies.init.StrategyInitParameter;
import com.becker.freelance.strategies.parameter.EntryParameter;
import com.becker.freelance.strategies.parameter.ExitParameter;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.trend.DownTrendIndicator;
import org.ta4j.core.num.DecimalNum;
import org.ta4j.core.num.Num;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class TrendTest extends BaseStrategy {

    private BarSeries barSeries;
    private TrendChanelIndicator upTrendIndicator;
    private DownTrendIndicator downTrendIndicator;
    private int period;

    public TrendTest() {
        super("trend", new PermutableStrategyInitParameter(List.of(
                new StrategyInitParameter("period", 5, 5, 5, 1)
        )));

    }

    public TrendTest(Map<String, Decimal> parameters) {
        super(parameters);

        barSeries = new BaseBarSeries();
        period = 10;
        int numForValidation = 3;
        Num errorRange = DecimalNum.valueOf(0.001);
        TrendIndicator trendIndicator = new TrendIndicator(barSeries, period, numForValidation, errorRange);
        upTrendIndicator = new TrendChanelIndicator(trendIndicator);
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new TrendTest(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {
        Bar currentPrice = entryParameter.currentPriceAsBar();
        barSeries.addBar(currentPrice);
        int barCount = barSeries.getBarCount();

        Optional<TrendChanel> value = upTrendIndicator.getValue(barCount - 1);

        value.ifPresent(chanel -> {
            System.out.println(chanel);
        });

//        System.out.println(currentPrice.getBeginTime() + " - " + currentPrice.getClosePrice() + " - Direction: " + up.direction());
        return Optional.empty();
    }

    private void print(BarSeries barSeries, Zone<?> support) {
        System.out.println(support);
        support.hits().stream()
                .sorted(Comparator.comparing(SwingPoint::index).reversed())
                .map(hit -> Map.entry(hit, barSeries.getBar(hit.index())))
                .forEach(bar -> {
                    System.out.println("\t\t" + bar.getValue().getBeginTime() + " - " + bar.getValue().getClosePrice() + " - " + bar.getKey().index());
                });
    }

    @Override
    public Optional<ExitSignal> shouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

    private record LastTwoMaResults(Double last, Double current) {
    }
}
