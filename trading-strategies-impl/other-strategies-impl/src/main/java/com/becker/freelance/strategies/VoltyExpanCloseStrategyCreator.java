package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.strategies.creation.ParameterName;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.creation.StrategyParameter;
import com.becker.freelance.strategies.creation.StringParameterName;
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
    public TradingStrategy build(Pair pair, StrategyParameter parameter) {
        return new VoltyExpanCloseStrategy(
                this, pair,
                parameter.getParameterAsInt(PERIOD),
                DecimalNum.valueOf(parameter.getParameterAsDouble(NUM_ATRS))
        );
    }
}
