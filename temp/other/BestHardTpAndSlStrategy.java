package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionBehaviour;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.executionparameter.ExitExecutionParameter;
import com.becker.freelance.strategies.strategy.BaseStrategy;
import com.becker.freelance.strategies.strategy.StrategyParameter;

import java.util.Optional;

public class BestHardTpAndSlStrategy extends BaseStrategy {

    private final boolean allBuy;
    private final Decimal tp;
    private final Decimal sl;

    public BestHardTpAndSlStrategy(StrategyParameter parameter, boolean allBuy, Decimal tp, Decimal sl) {
        super(parameter);
        this.allBuy = allBuy;
        this.tp = tp;
        this.sl = sl;
    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryExecutionParameter entryParameter) {


        return Optional.of(entrySignalFactory.fromDistance(Decimal.ONE, allBuy ? Direction.BUY : Direction.SELL, sl, tp, PositionBehaviour.HARD_LIMIT, entryParameter.currentPrice(), currentMarketRegime()));
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitExecutionParameter exitParameter) {
        return Optional.empty();
    }

}
