package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StrategyParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

public class TestStrategyCreator implements StrategyCreator {

    @Override
    public String strategyName() {
        return "Test";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters();
    }

    @Override
    public TradingStrategy build(Pair pair, StrategyParameter parameter) {
        return new TestStrategy(this, pair);
    }
}

