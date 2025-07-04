package com.becker.freelance.strategies.classification;

import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

public class ClassificationStrategyCreator implements StrategyCreator {

    private static final ParameterName TAKE_PROFIT_DELTA = new StringParameterName("takeProfitDelta");
    private static final ParameterName STOP_LOSS_DELTA = new StringParameterName("stopLossDelta");
    private static final ParameterName MIN_PROP_FOR_ENTRY = new StringParameterName("minPropForEntry");

    @Override
    public String strategyName() {
        return "classification_regression";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(

                new StrategyInitParameter(TAKE_PROFIT_DELTA, 5., 0., 100., 5.),
                new StrategyInitParameter(STOP_LOSS_DELTA, 5., 0., 100., 5.),
                new StrategyInitParameter(DefaultParameterNames.TRAILING_STOP_ORDER, 0, 0, 1, 1),
                new StrategyInitParameter(MIN_PROP_FOR_ENTRY, 0.7, 0.3, 0.9, 0.1)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new ClassificationStrategy(
                strategyParameter,
                strategyParameter.getParameterAsDouble(MIN_PROP_FOR_ENTRY),
                strategyParameter.getParameterAsDouble(TAKE_PROFIT_DELTA),
                strategyParameter.getParameterAsDouble(STOP_LOSS_DELTA),
                strategyParameter.getParameterAsBool(DefaultParameterNames.TRAILING_STOP_ORDER) ? PositionBehaviour.TRAILING : PositionBehaviour.HARD_LIMIT,
                new BufferedClassificationPredictor()
        );
    }
}
