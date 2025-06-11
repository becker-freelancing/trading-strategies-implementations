package com.becker.freelance.data;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Comparator;
import java.util.List;

public class IgDataRequestGold {

    private static final String MINUTE = "MINUTE";
    private static final String MINUTE_5 = "MINUTE_5";

    private static final String API_KEY = "735b3666f7b3bf52b5f92ad8a08ca4b6bcf86be3";
    private static final String IDENTIFIER = "beckerjason";
    private static String PASSWORD = "<set-by-first-program-argument>";
    private static final String API_URL = "https://demo-api.ig.com/gateway/deal";

    public static void main(String[] args) throws Exception {


        String epic = "CS.D.CFDGOLD.CFM.IP";
        String filename = "GLDUSD_5.csv";
        String resolution = MINUTE_5;
        int barsToRequest = 7500;

        LocalDateTime minTime = LocalDateTime.parse("2025-01-24T09:40");//LocalDateTime.of(2025, 1, 10, 0, 0, 0);//findMinTime(getCsvPath());
        PASSWORD = args[0];
        String securityToken = authenticate();
        System.out.println("Requesting to: " + minTime);
        if (securityToken != null) {
            String marketData = fetchMarketData(resolution, securityToken, minTime.minusMinutes(barsToRequest).plusHours(1), minTime.minusMinutes(1).plusHours(1), epic);
            parseAndWriteMarketData(marketData, filename);
        } else {
            System.out.println("Authentifizierung fehlgeschlagen.");
        }

        MissingTime.main(new String[]{filename});
    }

    public static void parseAndWriteMarketData(String marketData, String filename) throws IOException {

        Path path = getCsvPath(filename);
        List<String> lines = readCsv(path);
        JSONObject jsonObject = new JSONObject(marketData);
        JSONArray prices = jsonObject.getJSONArray("prices");

        for (Object o : prices) {
            JSONObject price = (JSONObject) o;
            String builder = price.getString("snapshotTimeUTC") + "," +
                    price.getJSONObject("openPrice").getDouble("bid") + "," +
                    price.getJSONObject("openPrice").getDouble("ask") + "," +
                    price.getJSONObject("highPrice").getDouble("bid") + "," +
                    price.getJSONObject("highPrice").getDouble("ask") + "," +
                    price.getJSONObject("lowPrice").getDouble("bid") + "," +
                    price.getJSONObject("lowPrice").getDouble("ask") + "," +
                    price.getJSONObject("closePrice").getDouble("bid") + "," +
                    price.getJSONObject("closePrice").getDouble("ask") + "," +
                    price.getDouble("lastTradedVolume");
            lines.add(builder);
        }

        Files.writeString(path, String.join("\n", lines));

        System.out.println("Abgefragte Punkte: " + prices.length());
        System.out.println("Übrigbleibende Punkte: " + jsonObject.getJSONObject("metadata").getJSONObject("allowance").getDouble("remainingAllowance"));
    }

    private static LocalDateTime findMinTime(Path path) throws IOException {
        List<String> lines = readCsv(path);
        return lines.stream().skip(1).map(line -> line.split(",")[0]).map(LocalDateTime::parse).min(Comparator.naturalOrder()).orElse(LocalDateTime.now());
    }

    private static List<String> readCsv(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path);
        return lines;
    }

    private static Path getCsvPath(String filename) {
        String pathString = "C:/Users/jasb/AppData/Roaming/krypto-java/.data-ig/" + filename;
        Path path = Path.of(pathString);
        return path;
    }

    private static String authenticate() throws Exception {
        URL url = new URL(API_URL + "/session");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
        conn.setRequestProperty("X-IG-API-KEY", API_KEY);
        conn.setRequestProperty("Accept", "application/json; charset=UTF-8");
        conn.setDoOutput(true);

        String payload = String.format("{\"identifier\":\"%s\", \"password\":\"%s\"}", IDENTIFIER, PASSWORD);
        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = payload.getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);
        }

        if (conn.getResponseCode() == 200) {
            String cstToken = conn.getHeaderField("CST");
            String xSecurityToken = conn.getHeaderField("X-SECURITY-TOKEN");
            return cstToken + ":" + xSecurityToken;
        } else {
            System.out.println("Fehler bei der Authentifizierung: " + conn.getResponseCode());
            return null;
        }
    }

    private static String fetchMarketData(String resolution, String securityToken, LocalDateTime fromTime, LocalDateTime toTime, String epic) throws Exception {
        URL url = new URL(API_URL + "/prices/" + epic + "?resolution=" + resolution + "&from=" + formatTime(fromTime) + "&to=" + formatTime(toTime) + "&max=3&pageSize=10000&pageNumber=0");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("X-IG-API-KEY", API_KEY);
        conn.setRequestProperty("CST", securityToken.split(":")[0]);
        conn.setRequestProperty("X-SECURITY-TOKEN", securityToken.split(":")[1]);
        conn.setRequestProperty("Accept", "application/json; charset=UTF-8");
        conn.setRequestProperty("Version", "3");

        if (conn.getResponseCode() == 200) {
            BufferedReader br = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = br.readLine()) != null) {
                response.append(line);
            }
            br.close();
            return response.toString();
        } else {
            System.out.println("Fehler beim Abrufen der Marktdaten: " + conn.getResponseCode());
            System.out.println(new String(conn.getErrorStream().readAllBytes()));
        }
        throw new RuntimeException();
    }

    private static String formatTime(LocalDateTime time) {
        String format = time.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        return format.replace(" ", "T").replaceAll(":", "%3A");
    }
}
