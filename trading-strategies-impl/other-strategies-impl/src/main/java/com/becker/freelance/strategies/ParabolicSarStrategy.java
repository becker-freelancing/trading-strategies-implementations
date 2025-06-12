package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.EntrySignalBuilder;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.commons.timeseries.TimeSeriesEntry;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import org.ta4j.core.indicators.ParabolicSarIndicator;
import org.ta4j.core.num.DecimalNum;

import java.time.LocalDateTime;
import java.util.Optional;

public class ParabolicSarStrategy extends BaseStrategy {


    private final ParabolicSarIndicator parabolicSarIndicator;
    private LocalDateTime lastUpdate = LocalDateTime.MIN;
    private Double currentSarValue;
    private Double lastSarValue;
    private Decimal currentCloseMid;
    private Decimal lastCloseMid;

    public ParabolicSarStrategy(StrategyParameter parameter, Double accelerationFactor, Double maxAccelerationFactor, int period) {
        super(parameter);
        this.barSeries.setMaximumBarCount(period);
        this.parabolicSarIndicator = new ParabolicSarIndicator(barSeries, DecimalNum.valueOf(accelerationFactor), DecimalNum.valueOf(maxAccelerationFactor));
    }

    @Override
    public Optional<EntrySignalBuilder> internalShouldEnter(EntryExecutionParameter entryParameter) {

        if (!lastUpdate.equals(entryParameter.time())) {
            calculateAndExtractInformation(entryParameter.timeSeries(), entryParameter.time());
        }
        if (lastSarValue.isNaN()) {
            return Optional.empty();
        }

        if (currentCloseMid.isLessThan(currentSarValue) && lastCloseMid.isGreaterThan(lastSarValue)) {
            return toSellEntrySignal(entryParameter.currentPrice());
        } else if (currentCloseMid.isGreaterThan(currentSarValue) && lastCloseMid.isLessThan(lastSarValue)) {
            return toBuyEntrySignal(entryParameter.currentPrice());
        }

        return Optional.empty();
    }

    public void calculateAndExtractInformation(TimeSeries timeSeries, LocalDateTime time) {

        int barCount = barSeries.getBarCount();
        currentSarValue = parabolicSarIndicator.getValue(barCount - 1).doubleValue();
        lastSarValue = parabolicSarIndicator.getValue(barCount - 2).doubleValue();

        currentCloseMid = timeSeries.getEntryForTime(time).getCloseMid();
        lastCloseMid = timeSeries.getLastEntryForTime(time).getCloseMid();

        lastUpdate = time;
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        calculateAndExtractInformation(exitParameter.timeSeries(), exitParameter.time());

        if (currentCloseMid.isLessThan(currentSarValue) && lastCloseMid.isGreaterThan(lastSarValue)) {
            //Alle Buy schließen
            return Optional.of(new ExitSignal(Direction.BUY));
        } else if (currentCloseMid.isGreaterThan(currentSarValue) && lastCloseMid.isLessThan(lastSarValue)) {
            //Alle Sell schließen
            return Optional.of(new ExitSignal(Direction.SELL));
        }

        return Optional.empty();
    }


    private Optional<EntrySignalBuilder> toBuyEntrySignal(TimeSeriesEntry currentPrice) {
        Decimal limit = currentCloseMid.add(currentCloseMid.subtract(currentSarValue).abs().multiply(2));

        return Optional.of(entrySignalBuilder()
                .withOpenMarketRegime(currentMarketRegime())
                .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                .withOpenOrder(orderBuilder().withDirection(Direction.BUY).asMarketOrder().withPair(currentPrice.pair()))
                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limit))
                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(new Decimal(currentSarValue))));
    }

    private Optional<EntrySignalBuilder> toSellEntrySignal(TimeSeriesEntry currentPrice) {
        Decimal limit = currentCloseMid.subtract(currentCloseMid.subtract(currentSarValue).abs().multiply(2));

        return Optional.of(entrySignalBuilder()
                .withOpenMarketRegime(currentMarketRegime())
                .withPositionBehaviour(PositionBehaviour.HARD_LIMIT)
                .withOpenOrder(orderBuilder().withDirection(Direction.SELL).asMarketOrder().withPair(currentPrice.pair()))
                .withLimitOrder(orderBuilder().asLimitOrder().withOrderPrice(limit))
                .withStopOrder(orderBuilder().asConditionalOrder().withDelegate(orderBuilder().asMarketOrder()).withThresholdPrice(new Decimal(currentSarValue))));
    }
}
