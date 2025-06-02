package com.becker.freelance.strategies;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.creation.StrategyCreator;
import com.becker.freelance.strategies.executionparameter.EntryParameter;
import com.becker.freelance.strategies.executionparameter.ExitParameter;

import java.util.Optional;

public class BestHardTpAndSlStrategy extends BaseStrategy{

    private final boolean allBuy;
    private final Decimal tp;
    private final Decimal sl;

    public BestHardTpAndSlStrategy(StrategyCreator strategyCreator, Pair pair, boolean allBuy, Decimal tp, Decimal sl) {
        super(strategyCreator, pair);
        this.allBuy = allBuy;
        this.tp = tp;
        this.sl = sl;
    }

    @Override
    public Optional<EntrySignal> internalShouldEnter(EntryParameter entryParameter) {


        return Optional.of(entrySignalFactory.fromDistance(Decimal.ONE, allBuy ? Direction.BUY : Direction.SELL, sl, tp, PositionType.HARD_LIMIT, entryParameter.currentPrice(), currentMarketRegime()));
    }

    @Override
    public Optional<ExitSignal> internalShouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

}
