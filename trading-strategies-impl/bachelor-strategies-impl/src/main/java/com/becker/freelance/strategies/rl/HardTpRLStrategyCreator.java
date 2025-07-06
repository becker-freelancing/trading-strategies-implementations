package com.becker.freelance.strategies.rl;

import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

public class HardTpRLStrategyCreator implements StrategyCreator {
    @Override
    public String strategyName() {
        return "RL_Strategy_Hard_TP_SL";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(DefaultParameterNames.TRAILING_STOP_ORDER, 0, 0, 1, 1),
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 5, 5, 200, 10),
                new StrategyInitParameter(DefaultParameterNames.TAKE_PROFIT, 5, 5, 200, 10)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new HardTpRLStrategy(
                strategyParameter,
                new BufferedRLPredictor(),
                strategyParameter.getParameterAsBool(DefaultParameterNames.TRAILING_STOP_ORDER) ? PositionBehaviour.TRAILING : PositionBehaviour.HARD_LIMIT,
                strategyParameter.getParameter(DefaultParameterNames.STOP_LOSS),
                strategyParameter.getParameter(DefaultParameterNames.TAKE_PROFIT)
        );
    }
}
