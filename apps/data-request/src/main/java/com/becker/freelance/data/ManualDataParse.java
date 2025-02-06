package com.becker.freelance.data;

import java.io.IOException;

public class ManualDataParse {

    public static void main(String[] args) throws IOException {

        String filename = "GLDUSD_5.csv";

        IgDataRequestGold.parseAndWriteMarketData(getData(), filename);

        MissingTime.main(new String[]{filename});
    }

    private static String getData() throws IOException {
        return new String(ManualDataParse.class.getClassLoader().getResource("content.txt").openStream().readAllBytes());
    }

}