package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.Direction;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import org.ta4j.core.Bar;
import org.ta4j.core.BarSeries;
import org.ta4j.core.BaseBarSeries;
import org.ta4j.core.indicators.ParabolicSarIndicator;
import org.ta4j.core.num.DecimalNum;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;

public class ParabolicSarStrategy extends BaseStrategy{

    public ParabolicSarStrategy(){
        super("Parabolic_SAR",
                new PermutableStrategyParameter(
                        new StrategyParameter("acceleration_factor", 0.04, 0.01, 0.07, 0.01),
                        new StrategyParameter("max_acceleration_factor", 0.2, 0.1, 0.5, 0.1),
                        new StrategyParameter("period", 100, 80, 400, 40),
                        new StrategyParameter("size", 0.5, 0.2, 1, 0.2)
                ));
    }

    private Double accelerationFactor;
    private Double maxAccelerationFactor;
    private int period;
    private Double size;


    private LocalDateTime lastUpdate = LocalDateTime.MIN;
    private Double currentSarValue;
    private Double lastSarValue;
    private Double currentCloseMid;
    private Double lastCloseMid;
    private BarSeries barSeries;
    private ParabolicSarIndicator parabolicSarIndicator;

    private ParabolicSarStrategy(Map<String, Double> parameters){
        this();
        this.accelerationFactor = parameters.get("acceleration_factor");
        this.maxAccelerationFactor = parameters.get("max_acceleration_factor");
        this.period = parameters.get("period").intValue();
        this.size = parameters.get("size");
        this.barSeries = new BaseBarSeries();
        this.barSeries.setMaximumBarCount(period);
        this.parabolicSarIndicator = new ParabolicSarIndicator(barSeries, DecimalNum.valueOf(accelerationFactor), DecimalNum.valueOf(maxAccelerationFactor));
    }

    @Override
    public BaseStrategy forParameters(Map<String, Double> parameters) {
        return new ParabolicSarStrategy(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {

        if (!lastUpdate.equals(time)){
            calculateAndExtractInformation(timeSeries, time);
        }
        if (lastSarValue.isNaN()){
            return Optional.empty();
        }

        if(currentCloseMid < currentSarValue && lastCloseMid > lastSarValue){
            return toSellEntrySignal();
        } else if (currentCloseMid > currentSarValue && lastCloseMid < lastSarValue) {
            return toBuyEntrySignal();
        }

        return Optional.empty();
    }

    public void calculateAndExtractInformation(TimeSeries timeSeries, LocalDateTime time){

        Bar currentBar = timeSeries.getEntryForTimeAsBar(time);
        barSeries.addBar(currentBar);

       int barCount = barSeries.getBarCount();
        currentSarValue = parabolicSarIndicator.getValue(barCount - 1).doubleValue();
        lastSarValue = parabolicSarIndicator.getValue(barCount - 2).doubleValue();

        currentCloseMid = timeSeries.getEntryForTime(time).getCloseMid();
        lastCloseMid = timeSeries.getLastEntryForTime(time).getCloseMid();

        lastUpdate = time;
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        calculateAndExtractInformation(timeSeries, time);

        if(currentCloseMid < currentSarValue && lastCloseMid > lastSarValue){
            //Alle Buy schließen
            return Optional.of(new ExitSignal(Double.MAX_VALUE, Direction.BUY));
        } else if (currentCloseMid > currentSarValue && lastCloseMid < lastSarValue) {
            //Alle Sell schließen
            return Optional.of(new ExitSignal(Double.MAX_VALUE, Direction.SELL));
        }

        return Optional.empty();
    }



    private Optional<EntrySignal> toBuyEntrySignal() {
        double stop = Math.abs(currentCloseMid - currentSarValue);
        return Optional.of(new EntrySignal(size, Direction.BUY, stop, stop * 2, PositionType.HARD_LIMIT));
    }

    private Optional<EntrySignal> toSellEntrySignal() {
        double stop = Math.abs(currentSarValue - currentCloseMid);
        return Optional.of(new EntrySignal(size, Direction.SELL, stop, stop * 2, PositionType.HARD_LIMIT));
    }
}
