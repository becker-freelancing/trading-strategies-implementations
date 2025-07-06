package com.becker.freelance.strategies.rl.read;

import com.becker.freelance.backtest.util.PathUtil;
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

public class BufferedRLPredictionReader {


    private static final Logger logger = LoggerFactory.getLogger(BufferedRLPredictionReader.class);

    private static final DateTimeFormatter PREDICTION_DATA_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private static Map<LocalDateTime, RLPrediction> PREDICTIONS = null;

    public static synchronized Map<LocalDateTime, RLPrediction> getPredictionsSingleton(String readPath) {
        if (PREDICTIONS == null) {
            logger.info("Start reading buffered prediction...");
            BufferedRLPredictionReader predictionReader = new BufferedRLPredictionReader();
            String path = PathUtil.fromRelativePath(readPath);
            PREDICTIONS = predictionReader.readPredictions(Path.of(path));
            logger.info("Finished reading buffered prediction.");
        }

        return PREDICTIONS;
    }

    public Map<LocalDateTime, RLPrediction> readPredictions(Path path) {
        try (Stream<String> lines = Files.lines(path)) {
            return lines.skip(1)
                    .parallel()
                    .map(line -> line.split(","))
                    .map(this::mapLine)
                    .collect(Collectors.toMap(RLPrediction::closeTime, o -> o));
        } catch (IOException e) {
            throw new IllegalStateException("Could not read prediction", e);
        }
    }

    private RLPrediction mapLine(String[] line) {
        LocalDateTime closeTime = LocalDateTime.parse(line[0], PREDICTION_DATA_FORMAT);
        Integer action = Integer.parseInt(line[1]);

        return new RLPrediction(
                closeTime,
                toRlAction(action)
        );
    }

    private RLAction toRlAction(Integer action) {
        return switch (action) {
            case 0 -> RLAction.NONE;
            case 1 -> RLAction.BUY;
            case 2 -> RLAction.SELL;
            case 3 -> RLAction.LIQUIDATE;
            default -> throw new IllegalStateException("Action " + action + " is not in [0, 1, 2, 3]");
        };
    }

    private Double[] parseDecimalList(String listContent) {
        return Arrays.stream(listContent.replaceAll("[\\[\\]\"]", "").split(" "))
                .map(String::trim)
                .map(Double::parseDouble)
                .toArray(Double[]::new);
    }
}
