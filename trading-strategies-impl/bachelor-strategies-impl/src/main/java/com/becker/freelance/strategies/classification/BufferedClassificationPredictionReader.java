package com.becker.freelance.strategies.classification;

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

public class BufferedClassificationPredictionReader {


    private static final Logger logger = LoggerFactory.getLogger(BufferedClassificationPredictionReader.class);

    private static final DateTimeFormatter PREDICTION_DATA_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private static Map<LocalDateTime, ClassificationPrediction> PREDICTIONS = null;

    public static synchronized Map<LocalDateTime, ClassificationPrediction> getPredictionsSingleton(String predictionPath) {
        if (PREDICTIONS == null) {
            logger.info("Start reading buffered prediction...");
            BufferedClassificationPredictionReader predictionReader = new BufferedClassificationPredictionReader();
            String path = PathUtil.fromRelativePath(predictionPath);
            PREDICTIONS = predictionReader.readPredictions(Path.of(path));
            logger.info("Finished reading buffered prediction.");
        }

        return PREDICTIONS;
    }

    public Map<LocalDateTime, ClassificationPrediction> readPredictions(Path path) {
        try (Stream<String> lines = Files.lines(path)) {
            return lines.skip(1)
                    .parallel()
                    .map(line -> line.split(","))
                    .map(this::mapLine)
                    .collect(Collectors.toMap(ClassificationPrediction::closeTime, o -> o));
        } catch (IOException e) {
            throw new IllegalStateException("Could not read prediction", e);
        }
    }

    private ClassificationPrediction mapLine(String[] line) {
        LocalDateTime closeTime = LocalDateTime.parse(line[0], PREDICTION_DATA_FORMAT);
        QuantileMarketRegime marketRegime = QuantileMarketRegime.fromId(Integer.parseInt(line[2]));
        Double[] prediction = parseDecimalList(line[3]);

        return new ClassificationPrediction(
                closeTime,
                prediction[0],
                prediction[1],
                prediction[2]
        );
    }

    private Double[] parseDecimalList(String listContent) {
        return Arrays.stream(listContent.replaceAll("[\\[\\]\"]", "").split(" "))
                .map(String::trim)
                .map(Double::parseDouble)
                .toArray(Double[]::new);
    }
}
