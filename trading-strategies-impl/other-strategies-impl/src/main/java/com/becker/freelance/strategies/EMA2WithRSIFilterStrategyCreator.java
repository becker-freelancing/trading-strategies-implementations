package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.*;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.LONG_MA_PERIOD;
import static com.becker.freelance.strategies.creation.DefaultParameterNames.SHORT_MA_PERIOD;

public class EMA2WithRSIFilterStrategyCreator implements StrategyCreator {

    private final ParameterName RSI_DIFF = new StringParameterName("rsiDiff");

    private static boolean shortMaLessThanLongMaValidation(StrategyCreationParameter parameter) {
        return parameter.getParameterAsInt(SHORT_MA_PERIOD) < parameter.getParameterAsInt(LONG_MA_PERIOD);
    }

    @Override
    public String strategyName() {
        return "2_EMA_Strategy_with_RSI_filter";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                EMA2WithRSIFilterStrategyCreator::shortMaLessThanLongMaValidation,
                new StrategyInitParameter(SHORT_MA_PERIOD, 5, 1, 20, 2),
                new StrategyInitParameter(LONG_MA_PERIOD, 7, 2, 50, 2),
                new StrategyInitParameter(DefaultParameterNames.RSI_PERIOD, 14, 10, 16, 2),
                new StrategyInitParameter(RSI_DIFF, 50, 40, 60, 10)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new EMA2WithRSIFilterStrategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(SHORT_MA_PERIOD),
                strategyParameter.getParameterAsInt(LONG_MA_PERIOD),
                strategyParameter.getParameterAsInt(DefaultParameterNames.RSI_PERIOD),
                strategyParameter.getParameterAsDouble(RSI_DIFF)
        );
    }
}
