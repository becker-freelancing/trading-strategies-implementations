package com.becker.freelance.backtest.resultviewer.app;

import com.becker.freelance.backtest.resultviewer.app.callback.ParsedBacktestResult;
import com.becker.freelance.backtest.resultviewer.app.callback.ParsedCallback;

import java.nio.file.Path;
import java.util.List;

public class BestParameterResultViewerApp {

    public static void main(String[] args) {

        new AbstractBacktestResultViewerApp(new ParameterParsedTradeConsumer()).run();
    }

    private static class ParameterParsedTradeConsumer implements ParsedCallback {

        @Override
        public void onBestCumulative(List<ParsedBacktestResult> bestCumulative, Path resultPath) {
            if (bestCumulative.isEmpty()) {
                return;
            }
            ParsedBacktestResult parsedBacktestResult = bestCumulative.get(0);

            String parametersJson = parsedBacktestResult.resultContent().parametersJson();
            String[] lines = parametersJson.split("\n");


            for (int i = 1; i < lines.length; i++) {
                String[] split = lines[i].split("\": ");
                String stratName = resultPath.getParent().getFileName().toString();

                String format = String.format("""
                        {
                            "strategyName": "%s",
                            "priority": 100,
                            "pair": "ETHPERP_1",
                            "regimes": [
                                %s"
                            ],
                            "parameters": "%s"
                        },
                        """, stratName, split[0], split[1]);
                System.out.println(format);
            }
        }

        @Override
        public void onBestMax(List<ParsedBacktestResult> bestMax, Path resultPath) {


        }

        @Override
        public void onBestMin(List<ParsedBacktestResult> bestMin, Path resultPath) {

        }

        @Override
        public void onMostTrades(List<ParsedBacktestResult> mostTrades, Path resultPath) {

        }

    }
}
