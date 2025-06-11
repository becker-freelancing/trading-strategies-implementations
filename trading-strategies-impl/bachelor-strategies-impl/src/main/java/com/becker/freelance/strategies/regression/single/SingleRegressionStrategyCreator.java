package com.becker.freelance.strategies.regression.single;

import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

public class SingleRegressionStrategyCreator implements StrategyCreator {

    private static final ParameterName TAKE_PROFIT_DELTA = new StringParameterName("takeProfitDelta");
    private static final ParameterName STOP_LOSS_DELTA = new StringParameterName("stopLossDelta");
    private static final ParameterName STOP_LOSS_NOT_PREDICTED_DELTA = new StringParameterName("stopLossNotPredictedDelta");

    @Override
    public String strategyName() {
        return "single_regression";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(TAKE_PROFIT_DELTA, 5., -20., 20., 2.),
                new StrategyInitParameter(STOP_LOSS_DELTA, 5., -20., 20., 2.),
                new StrategyInitParameter(STOP_LOSS_NOT_PREDICTED_DELTA, 5., 1., 20., 2.),
                new StrategyInitParameter(DefaultParameterNames.TRAILING_STOP_ORDER, 0, 0, 1, 1)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
//        return new SingleRegressionStrategy(
//                strategyParameter,
//                new BufferedSingleRegressionPredictor(),
//                strategyParameter.getParameter(TAKE_PROFIT_DELTA),
//                strategyParameter.getParameter(STOP_LOSS_DELTA),
//                strategyParameter.getParameter(STOP_LOSS_NOT_PREDICTED_DELTA),
//                strategyParameter.getParameterAsBool(DefaultParameterNames.TRAILING_STOP_ORDER) ? PositionBehaviour.TRAILING : PositionBehaviour.HARD_LIMIT
//        );

        throw new UnsupportedOperationException("Not implemented yet");
    }
}
