package com.becker.freelance.strategies.regression.sequence.shared;

import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;

import java.util.Optional;

public interface RegressionPredictor {

    public Optional<RegressionPrediction> predict(EntryExecutionParameter entryParameter);
}
