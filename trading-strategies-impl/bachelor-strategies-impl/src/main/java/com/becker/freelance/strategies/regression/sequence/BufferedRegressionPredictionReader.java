package com.becker.freelance.strategies.regression.sequence;

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

    private static Map<LocalDateTime, RegressionPrediction> PREDICTIONS = null;

    public static synchronized Map<LocalDateTime, RegressionPrediction> getPredictionsSingleton() {
        if (PREDICTIONS == null) {
            logger.info("Start reading buffered prediction...");
            BufferedRegressionPredictionReader predictionReader = new BufferedRegressionPredictionReader();
            String path = PathUtil.fromRelativePath("prediction-bybit/BACKTEST_PREDICTION_SEQUENCE_REGRESSION.csv");
            PREDICTIONS = predictionReader.readPredictions(Path.of(path));
            logger.info("Finished reading buffered prediction.");
        }

        return PREDICTIONS;
    }

    public Map<LocalDateTime, RegressionPrediction> readPredictions(Path path) {
        try (Stream<String> lines = Files.lines(path)) {
            return lines.skip(1)
                    .parallel()
                    .map(line -> line.split(","))
                    .map(this::mapLine)
                    .collect(Collectors.toMap(RegressionPrediction::closeTime, o -> o));
        } catch (IOException e) {
            throw new IllegalStateException("Could not read prediction", e);
        }
    }

    private RegressionPrediction mapLine(String[] line) {
        LocalDateTime closeTime = LocalDateTime.parse(line[0], PREDICTION_DATA_FORMAT);
        QuantileMarketRegime marketRegime = QuantileMarketRegime.fromId(Integer.parseInt(line[2]));
        Double[] prediction = parseDecimalList(line[3]);
        Double[] cumsumPrediction = parseDecimalList(line[4]);

        return new RegressionPrediction(
                closeTime,
                marketRegime,
                prediction,
                cumsumPrediction,
                new LogReturnInverseTransformerImpl(prediction)
        );
    }

    private Double[] parseDecimalList(String listContent) {
        return Arrays.stream(listContent.replaceAll("[\\[\\]\"]", "").split(" "))
                .map(String::trim)
                .map(Double::parseDouble)
                .toArray(Double[]::new);
    }
}
