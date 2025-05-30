package com.becker.freelance.strategies.regression.ml;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.position.PositionType;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;
import com.becker.freelance.strategies.init.PermutableStrategyInitParameter;
import com.becker.freelance.strategies.init.StrategyInitParameter;
import com.becker.freelance.strategies.parameter.EntryParameter;
import com.becker.freelance.strategies.parameter.ExitParameter;
import com.becker.freelance.strategies.regression.shared.BufferedPredictor;
import com.becker.freelance.strategies.regression.shared.PredictionToEntrySignalConverter;
import com.becker.freelance.strategies.regression.shared.TrailingStepFilter;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Predicate;

public abstract class MlBaseStrategy extends BaseStrategy {

    private BufferedPredictor predictor;
    private PredictionToEntrySignalConverter predictionToEntrySignalConverter;


    public MlBaseStrategy(String name) {
        super(name, new PermutableStrategyInitParameter(List.of(
                new StrategyInitParameter("stop_in_euro", new Decimal(10), new Decimal(10), new Decimal(100), new Decimal(10)),
                new StrategyInitParameter("limit_in_euro", new Decimal(10), new Decimal(10), new Decimal(200), new Decimal(10)),
                new StrategyInitParameter("size", new Decimal(1), new Decimal(0.2), new Decimal(1.2), new Decimal(0.2)),
                new StrategyInitParameter("trailing_enabled", new Decimal(1), new Decimal(0), new Decimal(1), new Decimal(1)),
                new StrategyInitParameter("trailing_step_euro", new Decimal(3), new Decimal(1), new Decimal(20), new Decimal(2))),
                MlBaseStrategy.stopLossLessThanTakeProfitFilter()));
    }
    public MlBaseStrategy(String name, String filename, Map<String, Decimal> parameters) {
        super(parameters);

        predictor = new BufferedPredictor(Pair.eurUsd1(), name, filename);
        Decimal stopLoss = parameters.get("stop_in_euro");
        Decimal takeProfit = parameters.get("limit_in_euro");
        Decimal size = parameters.get("size");
        PositionType positionType = parameters.get("trailing_enabled").isEqualTo(Decimal.ZERO) ? PositionType.TRAILING : PositionType.HARD_LIMIT;
        Decimal trailingStepSizeInEuro = parameters.get("trailing_step_euro");
        predictionToEntrySignalConverter = new PredictionToEntrySignalConverter(stopLoss, takeProfit, size, positionType, trailingStepSizeInEuro);
    }

    private static Predicate<Map<String, Decimal>> stopLossLessThanTakeProfitFilter() {
        Predicate<Map<String, Decimal>> stopLossTakeProfitFilter = parameters ->
                parameters.get("stop_in_euro").isLessThanOrEqualTo(parameters.get("limit_in_euro"));

        return new TrailingStepFilter("trailing_enabled", "trailing_step_euro", stopLossTakeProfitFilter);
    }

    @Override
    public Optional<EntrySignal> shouldEnter(EntryParameter entryParameter) {
        Optional<List<Decimal>> prediction = predictor.getPrediction(entryParameter.time());

        if (prediction.isEmpty()) {
            return Optional.empty();
        }

        return predictionToEntrySignalConverter.toEntrySignal(prediction.get(),
                entryParameter.pair(), entryParameter.currentPrice());
    }

    @Override
    public Optional<ExitSignal> shouldExit(ExitParameter exitParameter) {
        return Optional.empty();
    }

}
