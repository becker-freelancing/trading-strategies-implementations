package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreationParameter;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;

public class MA2StrategyCreator implements StrategyCreator {

    private static final ParameterName STOP_LOSS_DELTA = new StringParameterName("stopLossDelta");
    private static final ParameterName TAKE_PROFIT_DELTA = new StringParameterName("takeProfitDelta");

    private static boolean shortMaLessThanLongMaValidation(StrategyCreationParameter parameter) {
        return parameter.getParameterAsInt(SHORT_MA_PERIOD) < parameter.getParameterAsInt(LONG_MA_PERIOD) &&
                parameter.getParameter(STOP_LOSS_DELTA).isLessThan(parameter.getParameter(TAKE_PROFIT_DELTA));
    }

    @Override
    public String strategyName() {
        return "2_MA_Strategy";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                MA2StrategyCreator::shortMaLessThanLongMaValidation,
                new StrategyInitParameter(SHORT_MA_PERIOD, 5, 3, 15, 2),
                new StrategyInitParameter(LONG_MA_PERIOD, 7, 5, 20, 2),
                new StrategyInitParameter(SWING_HIGH_LOW_ORDER, 2, 1, 10, 2),
                new StrategyInitParameter(SWING_HIGH_LOW_MAX_AGE, 50, 10, 45, 10),
                new StrategyInitParameter(TRAILING_STOP_ORDER, 0, 0, 1, 1),
                new StrategyInitParameter(STOP_LOSS_DELTA, 0, 5, 100, 15),
                new StrategyInitParameter(TAKE_PROFIT_DELTA, 0, 5, 200, 15)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new MA2Strategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(SHORT_MA_PERIOD),
                strategyParameter.getParameterAsInt(LONG_MA_PERIOD),
                strategyParameter.getParameterAsInt(SWING_HIGH_LOW_MAX_AGE),
                strategyParameter.getParameterAsInt(SWING_HIGH_LOW_ORDER),
                strategyParameter.getParameter(STOP_LOSS_DELTA),
                strategyParameter.getParameter(TAKE_PROFIT_DELTA),
                strategyParameter.getParameterAsBool(TRAILING_STOP_ORDER) ? PositionBehaviour.TRAILING : PositionBehaviour.HARD_LIMIT
        );
    }
}
