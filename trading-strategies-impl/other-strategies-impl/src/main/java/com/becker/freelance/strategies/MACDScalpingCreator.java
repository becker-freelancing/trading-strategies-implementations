package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.DefaultParameterNames;
import com.becker.freelance.strategies.creation.StrategyCreationParameter;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;

public class MACDScalpingCreator implements StrategyCreator {

    private static boolean shortBarCountLessThanLongBarCountValidation(StrategyCreationParameter parameter) {
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
                new StrategyInitParameter(DefaultParameterNames.STOP_LOSS, 15, 10, 100, 20),
                new StrategyInitParameter(TAKE_PROFIT, 15, 10, 100, 20)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new MACDScalping(
                strategyParameter,
                strategyParameter.getParameterAsInt(LONG_MA_PERIOD),
                strategyParameter.getParameterAsInt(SHORT_MA_PERIOD),
                strategyParameter.getParameterAsInt(SIGNAL_LINE_PERIOD),
                strategyParameter.getParameter(STOP_LOSS),
                strategyParameter.getParameter(TAKE_PROFIT)
        );
    }
}
