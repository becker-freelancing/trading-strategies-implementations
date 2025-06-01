package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.*;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

public class BollingerBandBounceStrategyCreator implements StrategyCreator {

    private static final ParameterName STD = new StringParameterName("STD");

    @Override
    public String strategyName() {
        return "Bollinger_Band_Bounce";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(DefaultParameterNames.PERIOD, 14, 10, 25, 1),
                new StrategyInitParameter(STD, 2, 1.5, 3.0, 0.5),
                new StrategyInitParameter(DefaultParameterNames.SIZE, 0.5, 0.2, 1., 0.2)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter parameter) {
        return new BollingerBandBounceStrategy(
                this,
                parameter.getParameterAsInt(DefaultParameterNames.PERIOD),
                parameter.getParameter(STD),
                parameter.getParameter(DefaultParameterNames.SIZE)
        );
    }
}
