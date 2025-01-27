package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.Direction;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBar;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.EMAIndicator;
import org.ta4j.core.indicators.MACDIndicator;
import org.ta4j.core.indicators.helpers.ClosePriceIndicator;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class MACDScalping extends BaseStrategy{

    private static boolean shortBarCountLessThanLongBarCountValidation(Map<String, Double> parameter){
        return parameter.get("short_bar_count") < parameter.get("long_bar_count");
    }


    public MACDScalping() {
        super("MACD_Scalping", new PermutableStrategyParameter(List.of(
                new StrategyParameter("short_bar_count", 6, 5, 9, 2),
                new StrategyParameter("long_bar_count", 13, 11, 17, 2),
                new StrategyParameter("signal_line_period", 5, 2, 7, 2),
                new StrategyParameter("size", 0.5, 0.2, 1, 0.2),
                new StrategyParameter("take_profit", 15, 13, 22, 3),
                new StrategyParameter("stop_loss", 8, 6, 12, 2)
        ), MACDScalping::shortBarCountLessThanLongBarCountValidation));
    }

    private BarSeries barSeries;
    private MACDIndicator macdIndicator;
    private EMAIndicator macdSignal;
    private int longBarCount;
    private double stopLoss;
    private double takeProfit;
    private double size;

    public MACDScalping(Map<String, Double> parameters) {
        super(parameters);

        longBarCount = parameters.get("long_bar_count").intValue();
        barSeries = new BaseBarSeries();
        barSeries.setMaximumBarCount(longBarCount + 3);
        ClosePriceIndicator closePriceIndicator = new ClosePriceIndicator(barSeries);
        macdIndicator = new MACDIndicator(closePriceIndicator, parameters.get("short_bar_count").intValue(), longBarCount);
        macdSignal = new EMAIndicator(macdIndicator, parameters.get("signal_line_period").intValue());
        stopLoss = parameters.get("stop_loss");
        takeProfit = parameters.get("take_profit");
        size = parameters.get("size");
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Bar currentPrice = timeSeries.getEntryForTimeAsBar(time);
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
            return Optional.of(new EntrySignal(size, Direction.BUY, stopLoss, takeProfit, PositionType.HARD_LIMIT));
        } else if (currentMacd < currentSignal && lastMacd > lastSignal) {
            //SELL
            return Optional.of(new EntrySignal(size, Direction.SELL, stopLoss, takeProfit, PositionType.HARD_LIMIT));
        }

        return Optional.empty();
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Double> parameters) {
        return new MACDScalping(parameters);
    }
}
