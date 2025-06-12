package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
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
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 15, 10, 100, 20)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new BollingerBandBounceStrategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(DefaultParameterNames.PERIOD),
                strategyParameter.getParameter(STD),
                strategyParameter.getParameter(DefaultParameterNames.STOP_LOSS)
        );
    }
}
