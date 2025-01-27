package com.becker.freelance.data;


import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Comparator;
import java.util.List;

public class MissingTime {

    public static void main(String[] args) throws IOException {
        List<String> lines = readCsv(getCsvPath(args.length > 0 ? args[0] : "GLDUSD_1.csv"));
        List<LocalDateTime> times = lines.stream().skip(1).map(l -> l.split(",")[0]).map(LocalDateTime::parse).sorted().toList();

        LocalDateTime last = times.get(0);
        for(int i = 1; i < times.size(); i++){
            LocalDateTime curr = times.get(i);
            if (ChronoUnit.MINUTES.between(last, curr) > 1){
                if (last.getDayOfWeek() != DayOfWeek.FRIDAY || curr.getDayOfWeek() == DayOfWeek.FRIDAY){
                    System.out.println(last + "    -    " + curr + "    Diff: " + ChronoUnit.MINUTES.between(last, curr));
                }
            }
            last = curr;
        }
        System.out.println("Min: " + times.stream().min(Comparator.naturalOrder()).orElse(null));
        System.out.println("Max: " + times.stream().max(Comparator.naturalOrder()).orElse(null));
        System.out.println("Anz:" + times.size());
    }

    private static List<String> readCsv(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path);
        return lines;
    }

    private static Path getCsvPath(String filename) {
        String pathString = "C:\\Users\\jasb\\AppData\\Roaming\\krypto-java\\.data-ig\\" + filename;
        Path path = Path.of(pathString);
        return path;
    }
}
