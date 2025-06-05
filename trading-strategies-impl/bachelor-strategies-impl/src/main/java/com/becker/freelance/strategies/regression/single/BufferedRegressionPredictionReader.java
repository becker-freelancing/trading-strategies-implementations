package com.becker.freelance.strategies.regression.single;

import com.becker.freelance.backtest.util.PathUtil;
import com.becker.freelance.indicators.ta.regime.QuantileMarketRegime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class BufferedRegressionPredictionReader {

    private static final Logger logger = LoggerFactory.getLogger(BufferedRegressionPredictionReader.class);

    private static final DateTimeFormatter PREDICTION_DATA_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private static Map<LocalDateTime, SingleRegressionPrediction> PREDICTIONS = null;

    public static synchronized Map<LocalDateTime, SingleRegressionPrediction> getPredictionsSingleton() {
        if (PREDICTIONS == null) {
            logger.info("Start reading buffered prediction...");
            BufferedRegressionPredictionReader predictionReader = new BufferedRegressionPredictionReader();
            String path = PathUtil.fromRelativePath("prediction-bybit/BACKTEST_PREDICTION_SEQUENCE_REGRESSION.csv");
            PREDICTIONS = predictionReader.readPredictions(Path.of(path));
            logger.info("Finished reading buffered prediction.");
        }

        return PREDICTIONS;
    }

    public Map<LocalDateTime, SingleRegressionPrediction> readPredictions(Path path) {
        try (Stream<String> lines = Files.lines(path)) {
            return lines.skip(1)
                    .parallel()
                    .map(line -> line.split(","))
                    .map(this::mapLine)
                    .collect(Collectors.toMap(SingleRegressionPrediction::closeTime, o -> o));
        } catch (IOException e) {
            throw new IllegalStateException("Could not read prediction", e);
        }
    }

    private SingleRegressionPrediction mapLine(String[] line) {
        LocalDateTime closeTime = LocalDateTime.parse(line[0], PREDICTION_DATA_FORMAT);
        QuantileMarketRegime marketRegime = QuantileMarketRegime.fromId(Integer.parseInt(line[2]));
        Double[] prediction = parseDecimalList(line[3]);

        return new SingleRegressionPrediction(
                closeTime,
                marketRegime,
                prediction[0],
                prediction[1],
                new LogReturnInverseTransformerImpl(prediction[0]),
                new LogReturnInverseTransformerImpl(prediction[1])
        );
    }

    private Double[] parseDecimalList(String listContent) {
        return Arrays.stream(listContent.replaceAll("[\\[\\]\"]", "").split(" "))
                .map(String::trim)
                .map(Double::parseDouble)
                .toArray(Double[]::new);
    }
}
