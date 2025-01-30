package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.Direction;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.EuroDistanceEntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.math.Decimal;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class BestHardTpAndSlStrategy extends BaseStrategy{

    public BestHardTpAndSlStrategy(){
        super("Best_Hard_TP_and_SL", new PermutableStrategyParameter(List.of(
                new StrategyParameter("tp", 30, 50, 1000, 50),
                new StrategyParameter("sl", 15, 50, 1000, 50),
                new StrategyParameter("all_buy", 0, 0, 1, 1)
        )));
    }

    private boolean allBuy;
    private Decimal tp;
    private Decimal sl;

    public BestHardTpAndSlStrategy(Map<String, Decimal> parameters) {
        super(parameters);
        allBuy = !parameters.get("all_buy").isEqualToZero();
        tp = parameters.get("tp");
        sl = parameters.get("sl");
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {


        return Optional.of(new EuroDistanceEntrySignal(Decimal.ONE, allBuy ? Direction.BUY : Direction.SELL, sl, tp, PositionType.HARD_LIMIT));
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Decimal> parameters) {
        return new BestHardTpAndSlStrategy(parameters);
    }
}
