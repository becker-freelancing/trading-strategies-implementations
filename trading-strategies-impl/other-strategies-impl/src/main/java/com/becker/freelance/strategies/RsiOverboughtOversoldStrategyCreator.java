package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
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
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 15, 10, 100, 20),
                new StrategyInitParameter(TAKE_PROFIT, 15, 10, 100, 20)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new RsiOverboughtOversoldStrategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(RSI_PERIOD),
                strategyParameter.getParameter(TAKE_PROFIT),
                strategyParameter.getParameter(STOP_LOSS)
        );
    }
}
