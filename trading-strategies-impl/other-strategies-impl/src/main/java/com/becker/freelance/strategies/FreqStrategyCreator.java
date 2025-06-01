package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StrategyParameter;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;


public class FreqStrategyCreator implements StrategyCreator {

    private static boolean stopLessThanLimit(StrategyParameter parameters) {
        return parameters.getParameter(TAKE_PROFIT).isLessThanOrEqualTo(parameters.getParameter(STOP_LOSS));
    }

    @Override
    public String strategyName() {
        return "freq_strategy";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(FreqStrategyCreator::stopLessThanLimit,
                new StrategyInitParameter(SIZE, 1),//, 0.2, 1.2, 0.2),
                new StrategyInitParameter(SMA_PERIOD, 40, 30, 50, 10),
                new StrategyInitParameter(RSI_PERIOD, 14, 10, 18, 4),
                new StrategyInitParameter(STOCH_K_PERIOD, 14, 10, 18, 4),
                new StrategyInitParameter(STOP_LOSS, 10, 10, 40, 15),
                new StrategyInitParameter(TAKE_PROFIT, 20, 20, 60, 15)
        );
    }

    @Override
    public TradingStrategy build(Pair pair, StrategyParameter parameter) {
        return new FreqStrategy(
                this, pair,
                parameter.getParameterAsInt(SMA_PERIOD),
                parameter.getParameterAsInt(RSI_PERIOD),
                parameter.getParameterAsInt(STOCH_K_PERIOD),
                parameter.getParameter(SIZE),
                parameter.getParameter(STOP_LOSS),
                parameter.getParameter(TAKE_PROFIT)
        );
    }
}
