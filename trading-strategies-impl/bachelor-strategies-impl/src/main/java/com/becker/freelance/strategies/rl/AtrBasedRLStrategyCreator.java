package com.becker.freelance.strategies.rl;

import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

public class AtrBasedRLStrategyCreator implements StrategyCreator {

    private final static ParameterName ATR_MULTIPLIER = new StringParameterName("atrMultiplier");
    private final static ParameterName TAKE_PROFIT_MULTIPLIER = new StringParameterName("takeProfitMultiplier");


    @Override
    public String strategyName() {
        return "RL_Strategy_ATR";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(DefaultParameterNames.TRAILING_STOP_ORDER, 0, 0, 1, 1),
                new StrategyInitParameter(DefaultParameterNames.ATR_PERIOD, 5, 5, 20, 4),
                new StrategyInitParameter(ATR_MULTIPLIER, 0.8, 0.8, 2.5, 0.5),
                new StrategyInitParameter(TAKE_PROFIT_MULTIPLIER, 1.5, 1.5, 5., 0.5)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new AtrBasedRLStrategy(
                strategyParameter,
                new BufferedRLPredictor(),
                strategyParameter.getParameterAsBool(DefaultParameterNames.TRAILING_STOP_ORDER) ? PositionBehaviour.TRAILING : PositionBehaviour.HARD_LIMIT,
                strategyParameter.getParameterAsInt(DefaultParameterNames.ATR_PERIOD),
                strategyParameter.getParameter(ATR_MULTIPLIER),
                strategyParameter.getParameter(TAKE_PROFIT_MULTIPLIER)
        );
    }
}
