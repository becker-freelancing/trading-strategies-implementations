package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import java.util.List;

public class BestHardTpAndSlStrategyCreator implements StrategyCreator {

    private static final ParameterName ALL_BUY = new StringParameterName("allBuy");

    @Override
    public String strategyName() {
        return "Best_Hard_TP_and_SL";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(List.of(
                new StrategyInitParameter(DefaultParameterNames.TAKE_PROFIT, 30, 20, 300, 50),
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 15, 20, 300, 50),
                new StrategyInitParameter(ALL_BUY, 0, 0, 1, 1)
        ));
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new BestHardTpAndSlStrategy(
                strategyParameter,
                strategyParameter.getParameterAsBool(ALL_BUY),
                strategyParameter.getParameter(DefaultParameterNames.TAKE_PROFIT),
                strategyParameter.getParameter(DefaultParameterNames.STOP_LOSS)
        );
    }
}
