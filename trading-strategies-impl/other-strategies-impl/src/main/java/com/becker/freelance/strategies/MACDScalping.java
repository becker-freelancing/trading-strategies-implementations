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
import org.ta4j.core.indicators.EMAIndicator;
import org.ta4j.core.indicators.MACDIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.util.List;
import java.util.Map;
import java.util.Optional;

public class MACDScalping extends BaseStrategy{

    private static boolean shortBarCountLessThanLongBarCountValidation(Map<String, Decimal> parameter){
        return parameter.get("short_bar_count").isLessThan(parameter.get("long_bar_count"));
    }


    public MACDScalping() {
        super("MACD_Scalping", new PermutableStrategyInitParameter(List.of(
                new StrategyInitParameter("short_bar_count", 6, 5, 9, 2),
                new StrategyInitParameter("long_bar_count", 13, 11, 17, 2),
                new StrategyInitParameter("signal_line_period", 5, 2, 7, 2),
                new StrategyInitParameter("size", 0.5, 0.2, 1., 0.2),
                new StrategyInitParameter("limit_in_euros", 150, 130, 220, 30),
                new StrategyInitParameter("stop_in_euros", 80, 60, 120, 20)
        ), MACDScalping::shortBarCountLessThanLongBarCountValidation));
    }

    private BarSeries barSeries;
    private MACDIndicator macdIndicator;
    private EMAIndicator macdSignal;
    private int longBarCount;
    private Decimal stopInEuros;
    private Decimal limitInEuros;
    private Decimal size;

    public MACDScalping(Map<String, Decimal> parameters) {
        super(parameters);

        longBarCount = parameters.get("long_bar_count").intValue();
        barSeries = new BaseBarSeries();
        barSeries.setMaximumBarCount(longBarCount + 3);
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        macdIndicator = new MACDIndicator(closePriceIndicator, parameters.get("short_bar_count").intValue(), longBarCount);
        macdSignal = new EMAIndicator(macdIndicator, parameters.get("signal_line_period").intValue());
        stopInEuros = parameters.get("stop_in_euros");
        limitInEuros = parameters.get("limit_in_euros");
        size = parameters.get("size");
    }

    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {
        Bar currentPrice = entryParameter.currentPriceAsBar();
        barSeries.addBar(currentPrice);
        int barCount = barSeries.getBarCount();
        if (barCount < longBarCount){
            return Optional.empty();
        }
        double currentMacd = macdIndicator.getValue(barCount - 1).doubleValue();
        double lastMacd = macdIndicator.getValue(barCount - 2).doubleValue();
        double currentSignal = macdSignal.getValue(barCount - 1).doubleValue();
        double lastSignal = macdSignal.getValue(barCount - 2).doubleValue();

        if (currentMacd > currentSignal && lastMacd < lastSignal){
            //BUY
            return Optional.of(entrySignalFactory.fromAmount(size, Direction.BUY, stopInEuros, limitInEuros, PositionType.HARD_LIMIT, entryParameter.currentPrice()));
        } else if (currentMacd < currentSignal && lastMacd > lastSignal) {
            //SELL
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
        return new MACDScalping(parameters);
    }
}
