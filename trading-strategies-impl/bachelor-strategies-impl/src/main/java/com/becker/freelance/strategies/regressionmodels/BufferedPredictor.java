package com.becker.freelance.strategies.regressionmodels;

import com.becker.freelance.commons.PathUtil;
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
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.zip.ZipFile;

public class BufferedPredictor {

    private static final Logger logger = LoggerFactory.getLogger(BufferedPredictor.class);

    private final Map<LocalDateTime, List<Decimal>> predictions;

    protected BufferedPredictor(String modelName, int modelId) {
        String predictionFilePath = PathUtil.fromModelsDir("Datasource.HIST_DATA\\predictions_" + modelName + "_" + modelId + ".csv.zip");
        try {
            predictions = readPredictions(predictionFilePath);
        } catch (IOException e) {
            throw new IllegalStateException("Could not read prediction for model " + modelName + " with id " + modelId, e);
        }
    }

    protected Map<LocalDateTime, List<Decimal>> readPredictions(String predictionFilePath) throws IOException {
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

    private Map<LocalDateTime, List<Decimal>> mapPredictions(List<String[]> rows) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        return rows.stream().skip(1).parallel().map(row -> {
            LocalDateTime closeTime = LocalDateTime.parse(row[0], formatter);
            JSONArray predictionArray = new JSONArray(row[1]);
            List<Decimal> prediction = IntStream.range(0, predictions.size()).mapToObj(predictionArray::getDouble)
                    .map(Decimal::new)
                    .toList();
            return Map.entry(closeTime, prediction);
        }).collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    public Optional<List<Decimal>> getPrediction(LocalDateTime time) {
        return Optional.ofNullable(predictions.get(time));
    }
}
