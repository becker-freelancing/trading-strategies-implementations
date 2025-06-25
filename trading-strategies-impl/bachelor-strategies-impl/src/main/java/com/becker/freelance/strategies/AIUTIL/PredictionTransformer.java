package com.becker.freelance.strategies.AIUTIL;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class PredictionTransformer {

    public static void main(String[] args) throws Exception {

        Path path = Path.of("/home/jasonbecker/.config/krypto-java/prediction-bybit/BACKTEST_PREDICTION_SEQUENCE_REGRESSION.csv");

        List<String> lines = Files.readAllLines(path);
        String header = lines.remove(0);

        StringBuilder result = new StringBuilder();
        result.append(header).append("\n");

        for (String line : lines) {
            result.append(line);
            if (line.endsWith("\"")) {
                result.append("\n");
            }
        }

        Files.writeString(path, result);
    }
}
