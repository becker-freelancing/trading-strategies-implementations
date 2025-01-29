package com.becker.freelance.strategies.algorithm;

import com.becker.freelance.commons.timeseries.TimeSeriesEntry;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class SwingDetection {

    public Optional<TimeSeriesEntry> getLastSwingHigh(List<TimeSeriesEntry> values, int order) {
        List<Integer> swingHighs = findLocalExtrema(values, order, true);
        if (swingHighs.isEmpty()) {
            return Optional.empty();
        }
        int lastIndex = swingHighs.get(swingHighs.size() - 1);
        return Optional.of(values.get(lastIndex));
    }

    public Optional<TimeSeriesEntry> getLastSwingLow(List<TimeSeriesEntry> values, int order) {
        List<Integer> swingLows = findLocalExtrema(values, order, false);
        if (swingLows.isEmpty()) {
            return Optional.empty();
        }
        int lastIndex = swingLows.get(swingLows.size() - 1);
        return Optional.of(values.get(lastIndex));
    }

    private List<Integer> findLocalExtrema(List<TimeSeriesEntry> values, int order, boolean findHighs) {
        List<Integer> extrema = new ArrayList<>();
        int n = values.size();

        for (int i = order; i < n - order; i++) {
            boolean isExtrema = true;
            for (int j = 1; j <= order; j++) {
                if (findHighs) {
                    if (values.get(i).getCloseMid().isLessThanOrEqualTo(values.get(i - j).getCloseMid()) || values.get(i).getCloseMid().isLessThanOrEqualTo(values.get(i + j).getCloseMid())) {
                        isExtrema = false;
                        break;
                    }
                } else {
                    if (values.get(i).getCloseMid().isGreaterThanOrEqualTo(values.get(i - j).getCloseMid()) || values.get(i).getCloseMid().isGreaterThanOrEqualTo(values.get(i + j).getCloseMid())) {
                        isExtrema = false;
                        break;
                    }
                }
            }
            if (isExtrema) {
                extrema.add(Integer.valueOf(i));
            }
        }
        return extrema;
    }
}
