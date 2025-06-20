package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
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
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new SwingHighLowStrategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(DefaultParameterNames.SWING_HIGH_LOW_ORDER)
        );
    }
}
