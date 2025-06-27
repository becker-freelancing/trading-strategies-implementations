package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.StrategyCreationParameter;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.LONG_MA_PERIOD;
import static com.becker.freelance.strategies.creation.DefaultParameterNames.SHORT_MA_PERIOD;

public class EMA2SimpleStrategyCreator implements StrategyCreator {

    private static boolean shortMaLessThanLongMaValidation(StrategyCreationParameter parameter) {
        return parameter.getParameterAsInt(SHORT_MA_PERIOD) < parameter.getParameterAsInt(LONG_MA_PERIOD);
    }

    @Override
    public String strategyName() {
        return "2_EMA_Strategy_simple";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                EMA2SimpleStrategyCreator::shortMaLessThanLongMaValidation,
                new StrategyInitParameter(SHORT_MA_PERIOD, 5, 1, 20, 2),
                new StrategyInitParameter(LONG_MA_PERIOD, 7, 2, 50, 2)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new EMA2SimpleStrategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(SHORT_MA_PERIOD),
                strategyParameter.getParameterAsInt(LONG_MA_PERIOD)
        );
    }
}
