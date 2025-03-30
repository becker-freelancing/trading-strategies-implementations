package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.math.Decimal;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Random;

public class TestStrategy extends BaseStrategy {

    public TestStrategy() {
        super("Test", new PermutableStrategyParameter(
                List.of(
                        new StrategyParameter("min_vol", 1, 0, 10, 1),
                        new StrategyParameter("tp", 1, 30, 100, 10),
                        new StrategyParameter("sl", 1, 30, 50, 10)
                )
        ));
    }

    private TestStrategy(Map<String, Decimal> parameters){
        super(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Random rand = new Random();
        if (rand.nextDouble() < 0) {
            return Optional.empty();
        }
        Direction direction = rand.nextDouble() > 0.5 ? Direction.BUY : Direction.SELL;
        return Optional.of(entrySignalFactory.fromAmount(
                new Decimal(0.01), direction, Decimal.TEN, Decimal.ONE, PositionType.HARD_LIMIT, timeSeries.getEntryForTime(time)
        ));
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new TestStrategy(parameters);
    }
}

