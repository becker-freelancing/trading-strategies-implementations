package com.becker.freelance.strategies;

import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.Direction;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class BestHardTpAndSlStrategy extends BaseStrategy{

    public BestHardTpAndSlStrategy(){
        super("Best_Hard_TP_and_SL", new PermutableStrategyParameter(List.of(
                new StrategyParameter("tp", 30, 5, 100, 5),
                new StrategyParameter("sl", 15, 5, 100, 5),
                new StrategyParameter("all_buy", 0, 0, 1, 1)
        )));
    }

    private Double allBuy;
    private Double tp;
    private Double sl;

    public BestHardTpAndSlStrategy(Map<String, Double> parameters) {
        super(parameters);
        allBuy = parameters.get("all_buy");
        tp = parameters.get("tp");
        sl = parameters.get("sl");
    }

    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {


        return Optional.of(new EntrySignal(1, allBuy == 0 ? Direction.SELL : Direction.BUY, sl, tp, PositionType.HARD_LIMIT));
    }

    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    @Override
    public BaseStrategy forParameters(Map<String, Double> parameters) {
        return new BestHardTpAndSlStrategy(parameters);
    }
}
