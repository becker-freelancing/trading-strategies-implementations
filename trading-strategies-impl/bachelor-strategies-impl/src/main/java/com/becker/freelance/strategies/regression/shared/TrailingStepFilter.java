package com.becker.freelance.strategies.regression.shared;

import com.becker.freelance.math.Decimal;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.function.Predicate;

public class TrailingStepFilter implements Predicate<Map<String, Decimal>> {

    private final String trailingEnabledKey;
    private final String trailingStepSizeKey;
    private final Predicate<Map<String, Decimal>> otherFilter;
    private final Set<Map<String, Decimal>> executedNonTrailingConfigurations;

    public TrailingStepFilter(String trailingEnabledKey, String trailingStepSizeKey) {
        this(trailingEnabledKey, trailingStepSizeKey, map -> true);
    }

    public TrailingStepFilter(String trailingEnabledKey, String trailingStepSizeKey, Predicate<Map<String, Decimal>> otherFilter) {
        this.trailingEnabledKey = trailingEnabledKey;
        this.trailingStepSizeKey = trailingStepSizeKey;
        this.otherFilter = otherFilter;
        executedNonTrailingConfigurations = new HashSet<>();
    }

    @Override
    public boolean test(Map<String, Decimal> stringDecimalMap) {

        boolean testResult = testTrailingStep(stringDecimalMap);
        return testResult && otherFilter.test(stringDecimalMap);
    }

    private boolean testTrailingStep(Map<String, Decimal> stringDecimalMap) {
        if (stringDecimalMap.get(trailingEnabledKey).isEqualTo(Decimal.ONE)) {
            return true;
        }

        stringDecimalMap.remove(trailingStepSizeKey);

        if (executedNonTrailingConfigurations.contains(stringDecimalMap)) {
            return false;
        }

        executedNonTrailingConfigurations.add(stringDecimalMap);
        return true;
    }
}
