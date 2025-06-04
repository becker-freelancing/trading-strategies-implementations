package com.becker.freelance.strategies;

import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StringParameterName;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import com.becker.freelance.strategies.strategy.TradingStrategy;
import com.becker.freelance.strategies.validinitparameter.StrategyInitParameter;
import com.becker.freelance.strategies.validinitparameter.ValidStrategyInitParameters;
import org.ta4j.core.num.DecimalNum;

import static com.becker.freelance.strategies.creation.DefaultParameterNames.PERIOD;

public class VoltyExpanCloseStrategyCreator implements StrategyCreator {

    private static final ParameterName NUM_ATRS = new StringParameterName("numAtrs");


    @Override
    public String strategyName() {
        return "voltan_expan_close_strategy";
    }

    @Override
    public ValidStrategyInitParameters strategyParameters() {
        return new ValidStrategyInitParameters(
                new StrategyInitParameter(PERIOD, 5, 2, 10, 1),
                new StrategyInitParameter(NUM_ATRS, 0.75, 0.5, 1., 0.1)
        );
    }

    @Override
    public TradingStrategy build(StrategyParameter strategyParameter) {
        return new VoltyExpanCloseStrategy(
                strategyParameter,
                strategyParameter.getParameterAsInt(PERIOD),
                DecimalNum.valueOf(strategyParameter.getParameterAsDouble(NUM_ATRS))
        );
    }
}
