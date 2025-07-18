package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.StrategyCreationParameter;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;

public class MA2StrategyCreator implements StrategyCreator {

    private static boolean shortMaLessThanLongMaValidation(StrategyCreationParameter parameter) {
        return parameter.getParameterAsInt(SHORT_MA_PERIOD) < parameter.getParameterAsInt(LONG_MA_PERIOD);
    }

    @Override
    public String strategyName() {
        return "2_MA_Strategy";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                MA2StrategyCreator::shortMaLessThanLongMaValidation,
                new StrategyInitParameter(SHORT_MA_PERIOD, 5, 1, 10, 1),
                new StrategyInitParameter(LONG_MA_PERIOD, 20, 2, 20, 1),
                new StrategyInitParameter(SWING_HIGH_LOW_ORDER, 2, 1, 10, 1),
                new StrategyInitParameter(SWING_HIGH_LOW_MAX_AGE, 10, 5, 45, 10)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new MA2Strategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(SHORT_MA_PERIOD),
                strategyParameter.getParameterAsInt(LONG_MA_PERIOD),
                strategyParameter.getParameterAsInt(SWING_HIGH_LOW_MAX_AGE),
                strategyParameter.getParameterAsInt(SWING_HIGH_LOW_ORDER)
        );
    }
}
