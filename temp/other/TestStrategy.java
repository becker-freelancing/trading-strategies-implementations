package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;

import java.util.Optional;
import java.util.Random;

public class TestStrategy extends BaseStrategy {


    public TestStrategy(StrategyParameter parameter) {
        super(parameter);
    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryExecutionParameter entryParameter) {
        Random rand = new Random();
        if (rand.nextDouble() < 0) {
            return Optional.empty();
        }
        Direction direction = rand.nextDouble() > 0.5 ? Direction.BUY : Direction.SELL;
        return Optional.of(entrySignalFactory.fromAmount(
                new Decimal(0.01), direction, Decimal.TEN, Decimal.ONE, PositionBehaviour.HARD_LIMIT, entryParameter.currentPrice()
                , currentMarketRegime()
        ));
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }

}

