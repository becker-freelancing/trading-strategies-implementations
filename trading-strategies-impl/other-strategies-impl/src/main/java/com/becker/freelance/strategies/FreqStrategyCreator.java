package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.StrategyCreationParameter;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;


public class FreqStrategyCreator implements StrategyCreator {

    private static boolean stopLessThanLimit(StrategyCreationParameter parameters) {
        return parameters.getParameter(TAKE_PROFIT).isLessThanOrEqualTo(parameters.getParameter(STOP_LOSS));
    }

    @Override
    public String strategyName() {
        return "freq_strategy";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(FreqStrategyCreator::stopLessThanLimit,
                new StrategyInitParameter(SMA_PERIOD, 40, 30, 50, 10),
                new StrategyInitParameter(RSI_PERIOD, 14, 10, 18, 4),
                new StrategyInitParameter(STOCH_K_PERIOD, 14, 10, 18, 4),
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 15, 10, 100, 20),
                new StrategyInitParameter(TAKE_PROFIT, 15, 10, 100, 20)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new FreqStrategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(SMA_PERIOD),
                strategyParameter.getParameterAsInt(RSI_PERIOD),
                strategyParameter.getParameterAsInt(STOCH_K_PERIOD),
                strategyParameter.getParameter(STOP_LOSS),
                strategyParameter.getParameter(TAKE_PROFIT)
        );
    }
}
