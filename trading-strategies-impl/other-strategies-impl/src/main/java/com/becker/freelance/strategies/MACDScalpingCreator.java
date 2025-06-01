package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StrategyParameter;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;

public class MACDScalpingCreator implements StrategyCreator {

    private static boolean shortBarCountLessThanLongBarCountValidation(StrategyParameter parameter) {
        return parameter.getParameter(SHORT_MA_PERIOD).isLessThan(parameter.getParameter(LONG_MA_PERIOD));
    }

    @Override
    public String strategyName() {
        return "MACD_Scalping";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                MACDScalpingCreator::shortBarCountLessThanLongBarCountValidation,
                new StrategyInitParameter(SHORT_MA_PERIOD, 6, 5, 9, 2),
                new StrategyInitParameter(LONG_MA_PERIOD, 13, 11, 17, 2),
                new StrategyInitParameter(SIGNAL_LINE_PERIOD, 5, 2, 7, 2),
                new StrategyInitParameter(SIZE, 0.5, 0.2, 1., 0.2),
                new StrategyInitParameter(TAKE_PROFIT, 150, 130, 220, 30),
                new StrategyInitParameter(STOP_LOSS, 80, 60, 120, 20)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter parameter) {
        return new MACDScalping(
                this,
                parameter.getParameterAsInt(LONG_MA_PERIOD),
                parameter.getParameterAsInt(SHORT_MA_PERIOD),
                parameter.getParameterAsInt(SIGNAL_LINE_PERIOD),
                parameter.getParameter(STOP_LOSS),
                parameter.getParameter(TAKE_PROFIT),
                parameter.getParameter(SIZE)
        );
    }
}
