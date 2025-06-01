package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StrategyParameter;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;

public class RsiOverboughtOversoldStrategyCreator implements StrategyCreator {

    @Override
    public String strategyName() {
        return "Rsi_Overbought_Oversold";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(RSI_PERIOD, 12, 5, 17, 1),
                new StrategyInitParameter(STOP_LOSS, 90, 50, 150, 20),
                new StrategyInitParameter(TAKE_PROFIT, 110, 90, 220, 20),
                new StrategyInitParameter(SIZE, 0.5, 0.2, 1., 0.2)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter parameter) {
        return new RsiOverboughtOversoldStrategy(
                this,
                parameter.getParameterAsInt(RSI_PERIOD),
                parameter.getParameter(SIZE),
                parameter.getParameter(TAKE_PROFIT),
                parameter.getParameter(STOP_LOSS)
        );
    }
}
