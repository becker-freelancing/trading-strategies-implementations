package com.becker.freelance.strategies.regression.sequence;

import com.becker.freelance.indicators.ta.regime.QuantileMarketRegime;
import com.becker.freelance.strategies.executionparameter.EntryExecutionParameter;
import com.becker.freelance.strategies.regression.shared.PredictionParameter;
import com.freelance.becker.japy.api.JapyPort;
import com.freelance.becker.japy.api.MethodReturnValue;
import com.freelance.becker.japy.api.PythonMethod;
import com.freelance.becker.japy.api.PythonMethodArgument;
import com.freelance.becker.japy.api.exception.PythonMethodCallException;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

public class LiveRegressionPredictor implements RegressionPredictor {

    private final JapyPort japyPort;
    private final Map<QuantileMarketRegime, Integer> requiredInputLength;

    public LiveRegressionPredictor() {
        this.japyPort = JapyPort.getDefault();
        this.requiredInputLength = getRequiredInputLengths();
    }

    private Map<QuantileMarketRegime, Integer> getRequiredInputLengths() {
        PythonMethod pythonMethod = new PythonMethod("required_input_lengths");
        try {
            Optional<MethodReturnValue> optionalMethodReturnValue = japyPort.callMethod(pythonMethod);
            MethodReturnValue methodReturnValue = optionalMethodReturnValue.get();
            Map<String, Double> returnValue = (Map<String, Double>) methodReturnValue.getReturnValue();
            return returnValue.entrySet().stream()
                    .collect(Collectors.toMap(
                            entry -> QuantileMarketRegime.fromId(Integer.parseInt(entry.getKey())),
                            entry -> entry.getValue().intValue()
                    ));
        } catch (PythonMethodCallException e) {
            throw new IllegalStateException("Could not request required input lengths", e);
        }
    }

    @Override
    public Optional<RegressionPrediction> predict(EntryExecutionParameter parameter, PredictionParameter predictionParameter) {
        PythonMethod predict = new PythonMethod("predict", List.of(
                new PythonMethodArgument<>(predictionParameter.regimeId()),
                new PythonMethodArgument<>(predictionParameter.data())
        ));

        try {
            Optional<MethodReturnValue> methodReturnValue = japyPort.callMethod(predict);
            return methodReturnValue.map(returnValue -> map(returnValue, parameter, predictionParameter));
        } catch (PythonMethodCallException e) {
            throw new IllegalStateException(e);
        }
    }

    private RegressionPrediction map(MethodReturnValue methodReturnValue, EntryExecutionParameter parameter, PredictionParameter predictionParameter) {
        Double[] prediction = methodReturnValue.castListWithSameClassesExactly(Double.class).toArray(new Double[0]);
        return new RegressionPrediction(
                parameter.time(),
                predictionParameter.regime(),
                prediction,
                cumulate(prediction),
                new LogReturnInverseTransformerImpl(prediction)
        );
    }

    private Double[] cumulate(Double[] prediction) {
        Double[] cumulative = new Double[prediction.length];
        cumulative[0] = prediction[0];
        for (int i = 1; i < prediction.length; i++) {
            cumulative[i] = cumulative[i - 1] + prediction[i];
        }
        return cumulative;
    }

    @Override
    public boolean requiresPredictionParameter() {
        return true;
    }

    @Override
    public int requiredInputLengthForRegime(QuantileMarketRegime regime) {
        return requiredInputLength.get(regime);
    }

    @Override
    public int getMaxRequiredInputLength() {
        return requiredInputLength.values().stream().max(Comparator.naturalOrder()).orElse(1);
    }
}
