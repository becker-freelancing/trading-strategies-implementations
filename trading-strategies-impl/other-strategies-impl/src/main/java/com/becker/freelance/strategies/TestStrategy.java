package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;

import java.util.Optional;
import java.util.Random;

public class TestStrategy extends BaseStrategy {


    public TestStrategy(StrategyCreator strategyCreator, Pair pair) {
        super(strategyCreator, pair);
    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {
        Random rand = new Random();
        if (rand.nextDouble() < 0) {
            return Optional.empty();
        }
        Direction direction = rand.nextDouble() > 0.5 ? Direction.BUY : Direction.SELL;
        return Optional.of(entrySignalFactory.fromAmount(
                new Decimal(0.01), direction, Decimal.TEN, Decimal.ONE, PositionType.HARD_LIMIT, entryParameter.currentPrice()
                , currentMarketRegime()
        ));
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

}

