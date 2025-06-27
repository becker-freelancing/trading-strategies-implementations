package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreationParameter;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.LONG_MA_PERIOD;
import static com.becker.freelance.strategies.creation.DefaultParameterNames.SHORT_MA_PERIOD;

public class EMA2MinAtrStrategyCreator implements StrategyCreator {

    private static final ParameterName MIN_ATR = new StringParameterName("minAtrValue");

    private static boolean shortMaLessThanLongMaValidation(StrategyCreationParameter parameter) {
        return parameter.getParameterAsInt(SHORT_MA_PERIOD) < parameter.getParameterAsInt(LONG_MA_PERIOD);
    }

    @Override
    public String strategyName() {
        return "2_EMA_Strategy_min_ATR";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                EMA2MinAtrStrategyCreator::shortMaLessThanLongMaValidation,
                new StrategyInitParameter(SHORT_MA_PERIOD, 5, 1, 20, 2),
                new StrategyInitParameter(LONG_MA_PERIOD, 7, 2, 50, 2),
                new StrategyInitParameter(MIN_ATR, 1., 0.4, 2.5, 0.2)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new EMA2MinAtrStrategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(SHORT_MA_PERIOD),
                strategyParameter.getParameterAsInt(LONG_MA_PERIOD),
                strategyParameter.getParameterAsDouble(MIN_ATR)
        );
    }
}
