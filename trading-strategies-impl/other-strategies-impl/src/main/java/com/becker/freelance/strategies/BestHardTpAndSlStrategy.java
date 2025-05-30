package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.Direction;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.EntrySignalFactory;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.init.PermutableStrategyInitParameter;
import com.becker.freelance.strategies.init.StrategyInitParameter;
import com.becker.freelance.strategies.parameter.EntryParameter;
import com.becker.freelance.strategies.parameter.ExitParameter;

import java.util.List;
import java.util.Map;
import java.util.Optional;

public class BestHardTpAndSlStrategy extends BaseStrategy{

    public BestHardTpAndSlStrategy(){
        super("Best_Hard_TP_and_SL", new PermutableStrategyInitParameter(List.of(
                new StrategyInitParameter("tp", 30, 50, 1000, 50),
                new StrategyInitParameter("sl", 15, 50, 1000, 50),
                new StrategyInitParameter("all_buy", 0, 0, 1, 1)
        )));
    }

    private boolean allBuy;
    private Decimal tp;
    private Decimal sl;
    private EntrySignalFactory entrySignalFactory;

    public BestHardTpAndSlStrategy(Map<String, Decimal> parameters) {
        super(parameters);
        allBuy = !parameters.get("all_buy").isEqualToZero();
        tp = parameters.get("tp");
        sl = parameters.get("sl");
        entrySignalFactory = new EntrySignalFactory();
    }

    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {


        return Optional.of(entrySignalFactory.fromDistance(Decimal.ONE, allBuy ? Direction.BUY : Direction.SELL, sl, tp, PositionType.HARD_LIMIT, entryParameter.currentPrice()));
    }

    @Override
    public Optional<ExitSignal> shouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new BestHardTpAndSlStrategy(parameters);
    }
}
