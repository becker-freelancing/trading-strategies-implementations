package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.PERIOD;

public class ParabolicSarStrategyCreator implements StrategyCreator {

    private static final ParameterName ACC_FACTOR = new StringParameterName("accelerationFactor");
    private static final ParameterName MAX_ACC_FAcTOR = new StringParameterName("maxAccelerationFactor");

    @Override
    public String strategyName() {
        return "Parabolic_SAR";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(ACC_FACTOR, 0.04, 0.01, 0.07, 0.01),
                new StrategyInitParameter(MAX_ACC_FAcTOR, 0.2, 0.1, 0.5, 0.1),
                new StrategyInitParameter(PERIOD, 100, 80, 400, 40)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new ParabolicSarStrategy(
                strategyParameter,
                strategyParameter.getParameterAsDouble(ACC_FACTOR),
                strategyParameter.getParameterAsDouble(MAX_ACC_FAcTOR),
                strategyParameter.getParameterAsInt(PERIOD)
        );
    }
}
