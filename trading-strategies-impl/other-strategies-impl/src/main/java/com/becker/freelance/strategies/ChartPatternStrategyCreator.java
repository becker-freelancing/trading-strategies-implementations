package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.STOP_LOSS;
import static com.becker.freelance.strategies.creation.DefaultParameterNames.TAKE_PROFIT;

public class ChartPatternStrategyCreator implements StrategyCreator {

    @Override
    public String strategyName() {
        return "chart_pattern";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(STOP_LOSS, 50, 10, 100, 15),
                new StrategyInitParameter(TAKE_PROFIT, 120, 10, 100, 15)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new ChartPatternStrategy(
                strategyParameter,
                strategyParameter.getParameter(STOP_LOSS),
                strategyParameter.getParameter(TAKE_PROFIT)
        );
    }
}
