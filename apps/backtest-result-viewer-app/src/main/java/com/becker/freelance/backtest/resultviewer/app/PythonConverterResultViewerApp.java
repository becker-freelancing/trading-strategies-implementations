package com.becker.freelance.backtest.resultviewer.app;

import com.becker.freelance.backtest.resultviewer.app.callback.ParsedBacktestResult;
import com.becker.freelance.backtest.resultviewer.app.callback.ParsedCallback;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;
import java.util.stream.Collectors;

public class PythonConverterResultViewerApp {

    public static void main(String[] args) {

        new AbstractBacktestResultViewerApp(new PythonParsedTradeConsumer()).run();
    }

    private static class PythonParsedTradeConsumer implements ParsedCallback {

        @Override
        public void onBestCumulative(List<ParsedBacktestResult> bestCumulative, Path resultPath) {
            if (bestCumulative.isEmpty()) {
                return;
            }

            write(bestCumulative.get(0), resultPath, "BEST_CUM");
        }

        @Override
        public void onBestMax(List<ParsedBacktestResult> bestMax, Path resultPath) {
            if (bestMax.isEmpty()) {
                return;
            }

            write(bestMax.get(0), resultPath, "BEST_MAX");

        }

        @Override
        public void onBestMin(List<ParsedBacktestResult> bestMin, Path resultPath) {

            if (bestMin.isEmpty()) {
                return;
            }

            write(bestMin.get(0), resultPath, "BEST_MIN");
        }

        @Override
        public void onMostTrades(List<ParsedBacktestResult> mostTrades, Path resultPath) {

            if (mostTrades.isEmpty()) {
                return;
            }

            write(mostTrades.get(0), resultPath, "MOST_TRADES");
        }

        private void write(ParsedBacktestResult parsedBacktestResult, Path resultPath, String identifier) {
            String json = toJson(parsedBacktestResult);
            Path path = getPath(resultPath, identifier);
            try {
                if (!Files.exists(path)) {
                    Files.createFile(path);
                }
                Files.writeString(path, json, StandardCharsets.UTF_8, StandardOpenOption.WRITE);
            } catch (IOException e) {
                throw new IllegalStateException("Could not write File", e);
            }
        }

        private Path getPath(Path resultPath, String identifier) {
            return resultPath.getParent().resolve("PY_" + identifier + "_" + resultPath.getFileName().toString().replace(".csv.zst", ".json"));
        }

        private String toJson(ParsedBacktestResult result) {
            return "[" + result.trades().stream()
                    .map(trade -> String.format("{\"time\": \"%s\", \"pnl\": %s}", trade.time(), trade.pnl()))
                    .collect(Collectors.joining(",\n")) + "]";
        }
    }
}
