package com.becker.freelance.strategies.regression.ai;

import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.commons.signal.EntrySignal;
import com.becker.freelance.commons.signal.ExitSignal;
import com.becker.freelance.commons.timeseries.TimeSeries;
import com.becker.freelance.math.Decimal;
import com.becker.freelance.strategies.BaseStrategy;
import com.becker.freelance.strategies.PermutableStrategyParameter;
import com.becker.freelance.strategies.StrategyParameter;
import com.becker.freelance.strategies.regression.shared.BufferedPredictor;
import com.becker.freelance.strategies.regression.shared.PredictionToEntrySignalConverter;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public abstract class AbstractRegressionModelStrategy extends BaseStrategy {

    private Decimal size;
    private Decimal limitInEuro;
    private Decimal stopInEuro;
    private BufferedPredictor predictor;
    private PredictionToEntrySignalConverter predictionToEntrySignalConverter;

    public AbstractRegressionModelStrategy(String name) {
        super(name, new PermutableStrategyParameter(
                new StrategyParameter("size", 0.5, 0.2, 3., 0.2),
                new StrategyParameter("limit_in_euros", 150, 130, 220, 30),
                new StrategyParameter("stop_in_euros", 80, 60, 120, 20)
        ));
    }

    protected AbstractRegressionModelStrategy(Map<String, Decimal> parameters) {
        super(parameters);
        size = parameters.get("size");
        limitInEuro = parameters.get("limit_in_euros");
        stopInEuro = parameters.get("stop_in_euros");
        predictor = new BufferedPredictor(Pair.eurUsd1(), getModelName(), getModelId());
        predictionToEntrySignalConverter = new PredictionToEntrySignalConverter(stopInEuro, limitInEuro, size);
    }


    @Override
    public Optional<EntrySignal> shouldEnter(TimeSeries timeSeries, LocalDateTime time) {
        Optional<List<Decimal>> optionalPrediction = predictor.getPrediction(time);

        if (optionalPrediction.isEmpty()) {
            return Optional.empty();
        }

        List<Decimal> prediction = optionalPrediction.get();
        return predictionToEntrySignalConverter.toEntrySignal(prediction, timeSeries.getPair(), timeSeries.getEntryForTime(time));
    }


    @Override
    public Optional<ExitSignal> shouldExit(TimeSeries timeSeries, LocalDateTime time) {
        return Optional.empty();
    }

    protected abstract String getModelName();

    protected abstract int getModelId();
}
