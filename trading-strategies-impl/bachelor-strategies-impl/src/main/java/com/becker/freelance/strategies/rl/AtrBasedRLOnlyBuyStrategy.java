package com.becker.freelance.strategies.rl;

import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.strategy.StrategyParameter;
import org.ta4j.core.Indicator;
import org.ta4j.core.indicators.ATRIndicator;
import org.ta4j.core.num.Num;

public class AtrBasedRLOnlyBuyStrategy extends RLOnlyBuyStrategy {

    private final Indicator<Num> atr;
    private final Decimal atrMultiplier;
    private final Decimal takeProfitMultiplier;

    public AtrBasedRLOnlyBuyStrategy(StrategyParameter strategyParameter, RLPredictor rlPredictor, PositionBehaviour positionBehaviour, int atrPeriod, Decimal atrMultiplier, Decimal takeProfitMultiplier) {
        super(strategyParameter, rlPredictor, positionBehaviour);
        this.atr = new ATRIndicator(barSeries, atrPeriod);
        this.atrMultiplier = atrMultiplier;
        this.takeProfitMultiplier = takeProfitMultiplier;
    }

    @Override
    protected Decimal getStopDistance() {
        double atrValue = atr.getValue(barSeries.getEndIndex()).doubleValue();
        return Decimal.valueOf(atrValue).multiply(atrMultiplier);
    }

    @Override
    protected Decimal getLimitDistance(Decimal stopDistance) {
        return stopDistance.multiply(takeProfitMultiplier);
    }
}
