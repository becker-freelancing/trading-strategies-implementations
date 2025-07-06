package com.becker.freelance.strategies.rl;

import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.strategy.StrategyParameter;

public class HardTpRLStrategy extends RLStrategy {

    private final Decimal stopDistance;
    private final Decimal limitDistance;

    public HardTpRLStrategy(StrategyParameter strategyParameter, RLPredictor rlPredictor, PositionBehaviour positionBehaviour, Decimal stopDistance, Decimal limitDistance) {
        super(strategyParameter, rlPredictor, positionBehaviour);
        this.stopDistance = stopDistance;
        this.limitDistance = limitDistance;
    }

    @Override
    protected Decimal getStopDistance() {
        return stopDistance;
    }

    @Override
    protected Decimal getLimitDistance(Decimal stopDistance) {
        return limitDistance;
    }
}
