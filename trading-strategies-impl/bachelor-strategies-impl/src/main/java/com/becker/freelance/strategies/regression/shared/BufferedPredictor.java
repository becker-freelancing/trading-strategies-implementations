package com.becker.freelance.strategies.regression.shared;

import com.becker.freelance.commons.PathUtil;
import com.becker.freelance.commons.pair.Pair;
import com.becker.freelance.math.Decimal;
import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvException;
import org.json.JSONArray;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.io.InputStreamReader;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.zip.ZipFile;

public class BufferedPredictor {

    private static final Logger logger = LoggerFactory.getLogger(BufferedPredictor.class);

    private static Map<LocalDateTime, List<Decimal>> predictions;

    public BufferedPredictor(Pair pair, String modelName, int modelId) {
        this(pair, modelName, "prediction_" + modelName + "_" + modelId);
    }

    public BufferedPredictor(Pair pair, String modelName, String filename) {
        String predictionFilePath = PathUtil.fromModelsDir("HIST_DATA\\" + pair.shortName() + "\\" + modelName + "\\" + filename + ".csv.zip");
        try {
            predictions = readPredictions(predictionFilePath);
        } catch (IOException e) {
            throw new IllegalStateException("Could not read prediction in file " + filename, e);
        }
    }

    protected Map<LocalDateTime, List<Decimal>> readPredictions(String predictionFilePath) throws IOException {
        if (predictions != null) {
            return predictions;
        }
        logger.info("Start reading Prediction...");

        ZipFile zipFile = new ZipFile(predictionFilePath);
        CSVReader reader = new CSVReader(new InputStreamReader(zipFile.getInputStream(zipFile.entries().nextElement())));

        List<String[]> rows = null;
        try {
            rows = reader.readAll();
        } catch (CsvException e) {
            throw new IOException(e);
        }


        Map<LocalDateTime, List<Decimal>> predictions = mapPredictions(rows);
        logger.info("Prediction loaded");
        return predictions;
    }

    private static List<Decimal> mapPrediction(String predictionString) {
        try {
            return mapJsonPrediction(predictionString);
        } catch (Exception e) {
            return mapPandasPrediction(predictionString);
        }
    }

    private static List<Decimal> mapPandasPrediction(String predictionString) {
        if (predictionString.startsWith("[")) {
            predictionString = predictionString.substring(1);
        }
        if (predictionString.endsWith("]")) {
            predictionString = predictionString.substring(0, predictionString.length() - 1);
        }

        String[] decimals = predictionString.split(" ");
        return Arrays.stream(decimals)
                .map(String::trim)
                .filter(s -> !s.isBlank())
                .map(s -> s.replace("\n", ""))
                .map(Decimal::new)
                .toList();
    }

    private static List<Decimal> mapJsonPrediction(String predictionString) {
        JSONArray predictionArray = new JSONArray(predictionString);
        List<Decimal> prediction = IntStream.range(0, predictionArray.length()).mapToObj(predictionArray::getDouble)
                .map(Decimal::new)
                .toList();
        return prediction;
    }

    private Map<LocalDateTime, List<Decimal>> mapPredictions(List<String[]> rows) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        return rows.stream().skip(1).parallel().map(row -> {
            LocalDateTime closeTime = LocalDateTime.parse(row[0], formatter);
            List<Decimal> prediction = mapPrediction(row[1]);
            return Map.entry(closeTime, prediction);
        }).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    public Optional<List<Decimal>> getPrediction(LocalDateTime time) {
        return Optional.ofNullable(predictions.get(time));
    }
}
