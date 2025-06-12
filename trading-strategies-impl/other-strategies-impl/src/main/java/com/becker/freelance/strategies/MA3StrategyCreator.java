package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.*;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;

public class MA3StrategyCreator implements StrategyCreator {

    private static final ParameterName MIN_SLOPE = new StringParameterName("minSlope");
    private static final ParameterName MIN_SLOPE_WINDOW = new StringParameterName("minSlopeWindow");

    private static boolean validateParameter(StrategyCreationParameter parameters) {
        return parameters.getParameter(SHORT_MA_PERIOD).isLessThan(parameters.getParameter(MID_MA_PERIOD)) &&
                parameters.getParameter(MID_MA_PERIOD).isLessThan(parameters.getParameter(LONG_MA_PERIOD));
    }


    @Override
    public String strategyName() {
        return "3_Ma_Strategy";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(MA3StrategyCreator::validateParameter,
                new StrategyInitParameter(SHORT_MA_PERIOD, 5, 3, 9, 3),
                new StrategyInitParameter(MID_MA_PERIOD, 20, 10, 30, 10),
                new StrategyInitParameter(LONG_MA_PERIOD, 200, 150, 250, 50),
                new StrategyInitParameter(MIN_SLOPE, 1, 0.4, 0.8, 0.4),
                new StrategyInitParameter(MIN_SLOPE_WINDOW, 20, 20, 40, 20),
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 15, 10, 100, 20),
                new StrategyInitParameter(TAKE_PROFIT, 15, 10, 100, 20)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new MA3Strategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(LONG_MA_PERIOD),
                strategyParameter.getParameterAsInt(SHORT_MA_PERIOD),
                strategyParameter.getParameterAsInt(MID_MA_PERIOD),
                strategyParameter.getParameter(MIN_SLOPE),
                strategyParameter.getParameterAsInt(MIN_SLOPE_WINDOW),
                strategyParameter.getParameter(STOP_LOSS),
                strategyParameter.getParameter(TAKE_PROFIT)
        );
    }
}
