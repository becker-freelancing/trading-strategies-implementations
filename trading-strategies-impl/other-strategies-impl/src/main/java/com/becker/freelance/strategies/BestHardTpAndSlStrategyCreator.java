package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.strategies.creation.*;
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
                new StrategyInitParameter(DefaultParameterNames.TAKE_PROFIT, 30, 50, 1000, 50),
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 15, 50, 1000, 50),
                new StrategyInitParameter(ALL_BUY, 0, 0, 1, 1)
        ));
    }

    @Override
    public TradingStrategy build(Pair pair, StrategyParameter parameter) {
        return new BestHardTpAndSlStrategy(
                this, pair,
                parameter.getParameterAsBool(ALL_BUY),
                parameter.getParameter(DefaultParameterNames.TAKE_PROFIT),
                parameter.getParameter(DefaultParameterNames.STOP_LOSS)
        );
    }
}
