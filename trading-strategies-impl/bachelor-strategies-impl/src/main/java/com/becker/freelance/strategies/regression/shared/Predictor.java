package com.becker.freelance.strategies.regression.shared;

import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;

import java.util.Optional;

public interface Predictor<T> {

    public Optional<T> predict(EntryExecutionParameter parameter)
}
