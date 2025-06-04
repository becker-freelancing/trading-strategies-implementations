package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.*;

public class SuperTrendStrategyCreator implements StrategyCreator {

    private static final ParameterName rsi_k = new StringParameterName("rsi_k");
    private static final ParameterName rsi_d = new StringParameterName("rsi_d");
    private static final ParameterName rsi_stoch_length = new StringParameterName("rsi_stoch_length");
    private static final ParameterName rsi_cross_max_age = new StringParameterName("rsi_cross_max_age");
    private static final ParameterName risk_ratio = new StringParameterName("risk_ratio");
    private static final ParameterName max_rsi_diff = new StringParameterName("max_rsi_diff");
    private static final ParameterName supertrend_1_atr = new StringParameterName("supertrend_1_atr");
    private static final ParameterName supertrend_1_multiplier = new StringParameterName("supertrend_1_multiplier");
    private static final ParameterName supertrend_2_atr = new StringParameterName("supertrend_2_atr");
    private static final ParameterName supertrend_2_multiplier = new StringParameterName("supertrend_2_multiplier");
    private static final ParameterName supertrend_3_atr = new StringParameterName("supertrend_3_atr");
    private static final ParameterName supertrend_3_multiplier = new StringParameterName("supertrend_3_multiplier");

    @Override
    public String strategyName() {
        return "super_trend";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(rsi_k, 3),
                new StrategyInitParameter(rsi_d, 3),
                new StrategyInitParameter(RSI_PERIOD, 14, 13, 15, 1),
                new StrategyInitParameter(rsi_stoch_length, 14),
                new StrategyInitParameter(rsi_cross_max_age, 5, 5, 15, 5),
                new StrategyInitParameter(SIZE, 0.2, 0.2, 1.2, 0.2),
                new StrategyInitParameter(risk_ratio, 1.5, 1., 2., 0.2),
                new StrategyInitParameter(max_rsi_diff, 20, 0, 30, 10),
                new StrategyInitParameter(EMA_PERIOD, 200),
                new StrategyInitParameter(supertrend_1_atr, 10),
                new StrategyInitParameter(supertrend_1_multiplier, 1),
                new StrategyInitParameter(supertrend_2_atr, 11),
                new StrategyInitParameter(supertrend_2_multiplier, 2),
                new StrategyInitParameter(supertrend_3_atr, 12),
                new StrategyInitParameter(supertrend_3_multiplier, 3)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new SuperTrendStrategy(
                strategyParameter,
                strategyParameter.getParameterAsDouble(max_rsi_diff),
                strategyParameter.getParameterAsInt(rsi_cross_max_age),
                strategyParameter.getParameterAsDouble(risk_ratio),
                strategyParameter.getParameter(SIZE),
                strategyParameter.getParameterAsInt(EMA_PERIOD),
                strategyParameter.getParameterAsInt(RSI_PERIOD),
                strategyParameter.getParameterAsInt(rsi_stoch_length),
                strategyParameter.getParameterAsInt(rsi_k),
                strategyParameter.getParameterAsInt(rsi_d),
                strategyParameter.getParameterAsInt(supertrend_1_atr),
                strategyParameter.getParameterAsDouble(supertrend_1_multiplier),
                strategyParameter.getParameterAsInt(supertrend_2_atr),
                strategyParameter.getParameterAsDouble(supertrend_2_multiplier),
                strategyParameter.getParameterAsInt(supertrend_3_atr),
                strategyParameter.getParameterAsDouble(supertrend_3_multiplier)
        );
    }
}
