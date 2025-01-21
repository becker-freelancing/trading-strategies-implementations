package com.becker.freelance.strategies;

import com.becker.freelance.commons.*;
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
                        new StrategyParameter("tp", 1, 0, 100, 10),
                        new StrategyParameter("sl", 1, 0, 50, 10)
                )
        ));
    }

    private TestStrategy(Map<String, Double> parameters){
        super(parameters);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Random rand = new Random();
        if (rand.nextDouble() > 0.2) {
            return Optional.empty();
        }
        Direction direction = rand.nextDouble() > 0.5 ? Direction.BUY : Direction.SELL;
        return Optional.of(new EntrySignal(
                1, direction, 10, 1, PositionType.HARD_LIMIT
        ));
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Double> parameters) {
        return new TestStrategy(parameters);
    }
}

