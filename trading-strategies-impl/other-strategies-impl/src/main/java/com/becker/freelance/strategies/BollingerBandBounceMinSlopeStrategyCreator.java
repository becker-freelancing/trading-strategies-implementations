package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.strategies.creation.*;
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
                new StrategyInitParameter(DefaultParameterNames.PERIOD, 14, 15, 20, 1),
                new StrategyInitParameter(STD, 2, 1., 1.8, 0.2),
                new StrategyInitParameter(DefaultParameterNames.SIZE, 0.5, 0.2, 1., 0.2),
                new StrategyInitParameter(MIN_SLOPE, 1, 0.2, 1.0, 0.4),
                new StrategyInitParameter(MIN_SLOPE_WINDOW, 20, 20, 70, 10),
                new StrategyInitParameter(MIN_SLOPE_PERIOD, 20, 20, 40, 10));
    }

    @Override
    public TradingStrategy build(Pair pair, StrategyParameter parameter) {
        return new BollingerBandBounceMinSlopeStrategy(
                this, pair,
                parameter.getParameterAsInt(DefaultParameterNames.PERIOD),
                parameter.getParameter(STD),
                parameter.getParameter(DefaultParameterNames.SIZE),
                parameter.getParameter(MIN_SLOPE),
                parameter.getParameterAsInt(MIN_SLOPE_WINDOW),
                parameter.getParameterAsInt(MIN_SLOPE_PERIOD)
        );
    }
}
