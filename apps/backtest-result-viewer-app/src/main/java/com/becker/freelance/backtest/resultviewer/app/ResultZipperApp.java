package com.becker.freelance.backtest.resultviewer.app;

import com.becker.freelance.backtest.commons.BacktestResultZipper;
import com.becker.freelance.backtest.util.PathUtil;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Stream;

public class ResultZipperApp {

    public static void main(String[] args) throws IOException {
        Path resultDir = Path.of(PathUtil.rootResultDir());
        try (Stream<Path> walk = Files.walk(resultDir)){
            List<Path> list = walk.filter(Files::isRegularFile).filter(p -> p.toString().endsWith(".csv")).toList();
            PropertyAsker propertyAsker = new PropertyAsker();
            Path path = propertyAsker.askProperty(list, p -> p.getFileName().toString(), "Path");
            new BacktestResultZipper(path).zipFile();
        }
    }
}
