package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StrategyParameter;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

public class SwingHighLowStrategyCreator implements StrategyCreator {

    @Override
    public String strategyName() {
        return "swing_high_low";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(DefaultParameterNames.SWING_HIGH_LOW_ORDER, 2, 2, 10, 1)
        );
    }

    @Override
    public TradingStrategy build(Pair pair, StrategyParameter parameter) {
        return new SwingHighLowStrategy(
                this, pair,
                parameter.getParameterAsInt(DefaultParameterNames.SWING_HIGH_LOW_ORDER)
        );
    }
}
