package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StrategyParameter;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;

public class ChartPatternStrategyCreator implements StrategyCreator {

    @Override
    public String strategyName() {
        return "chart_pattern";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(SIZE, 1, 0.02, 0.02, 0.02),
                new StrategyInitParameter(STOP_LOSS, 50, 10, 100, 15),
                new StrategyInitParameter(TAKE_PROFIT, 120, 10, 100, 15)
        );
    }

    @Override
    public TradingStrategy build(Pair pair, StrategyParameter parameter) {
        return new ChartPatternStrategy(
                this, pair,
                parameter.getParameter(SIZE),
                parameter.getParameter(STOP_LOSS),
                parameter.getParameter(TAKE_PROFIT)
        );
    }
}
