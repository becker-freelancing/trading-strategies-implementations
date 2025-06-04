package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.strategies.TradingStrategy;
import com.becker.freelance.strategies.creation.*;
import com.becker.freelance.strategies.regression.sequence.shared.BufferedRegressionPredictor;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

public class SequenceRegressionStrategyCreator implements StrategyCreator {

    private static final ParameterName TAKE_PROFIT_DELTA = new StringParameterName("takeProfitDelta");
    private static final ParameterName STOP_LOSS_DELTA = new StringParameterName("stopLossDelta");
    private static final ParameterName STOP_LOSS_NOT_PREDICTED_DELTA = new StringParameterName("stopLossNotPredictedDelta");

    @Override
    public String strategyName() {
        return "sequence_regression";
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
    public TradingStrategy build(Pair pair, StrategyParameter parameter) {
        return new SequenceRegressionStrategy(
                this,
                pair,
                new BufferedRegressionPredictor(),
                parameter.getParameter(TAKE_PROFIT_DELTA),
                parameter.getParameter(STOP_LOSS_DELTA),
                parameter.getParameter(STOP_LOSS_NOT_PREDICTED_DELTA),
                parameter.getParameterAsBool(DefaultParameterNames.TRAILING_STOP_ORDER) ? PositionType.TRAILING : PositionType.HARD_LIMIT
        );
    }
}
