package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.PositionBehaviour;
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
                new StrategyInitParameter(SHORT_MA_PERIOD, 5, 3, 10, 2),
                new StrategyInitParameter(MID_MA_PERIOD, 20, 5, 30, 3),
                new StrategyInitParameter(LONG_MA_PERIOD, 200, 10, 50, 5),
                new StrategyInitParameter(MIN_SLOPE, 1, 0.2, 1.2, 0.2),
                new StrategyInitParameter(MIN_SLOPE_WINDOW, 20, 10, 40, 10),
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 15, 10, 100, 10),
                new StrategyInitParameter(TAKE_PROFIT, 15, 10, 150, 10),
                new StrategyInitParameter(TRAILING_STOP_ORDER, 0, 0, 1, 1)
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
                strategyParameter.getParameter(TAKE_PROFIT),
                strategyParameter.getParameterAsBool(TRAILING_STOP_ORDER) ? PositionBehaviour.TRAILING : PositionBehaviour.HARD_LIMIT
        );
    }
}
