package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

public class BollingerBandBounceMinSlopeStrategyCreator implements StrategyCreator {

    private static final ParameterName STD = new StringParameterName("std");
    private static final ParameterName MIN_SLOPE = new StringParameterName("minSlope");
    private static final ParameterName MIN_SLOPE_WINDOW = new StringParameterName("minSlopeWindow");
    private static final ParameterName MIN_SLOPE_PERIOD = new StringParameterName("minSlopePeriod");

    @Override
    public String strategyName() {
        return "Bollinger_Band_Bounce_Min_Slope";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(DefaultParameterNames.PERIOD, 14, 15, 20, 2),
                new StrategyInitParameter(STD, 2, 1., 1.8, 0.2),
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 15, 10, 100, 20),
                new StrategyInitParameter(MIN_SLOPE, 1, 0.2, 1.0, 0.4),
                new StrategyInitParameter(MIN_SLOPE_WINDOW, 20, 20, 70, 15),
                new StrategyInitParameter(MIN_SLOPE_PERIOD, 20, 20, 40, 15));
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new BollingerBandBounceMinSlopeStrategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(DefaultParameterNames.PERIOD),
                strategyParameter.getParameter(STD),
                strategyParameter.getParameter(MIN_SLOPE),
                strategyParameter.getParameterAsInt(MIN_SLOPE_WINDOW),
                strategyParameter.getParameterAsInt(MIN_SLOPE_PERIOD),
                strategyParameter.getParameter(DefaultParameterNames.STOP_LOSS)
        );
    }
}
