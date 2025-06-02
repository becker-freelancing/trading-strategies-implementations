package com.becker.freelance.strategies.regression.sequence.shared;

import com.becker.freelance.strategies.executionparameter.EntryParameter;

import java.util.Optional;

public interface RegressionPredictor {

    public Optional<RegressionPrediction> predict(EntryParameter entryParameter);
}
