package com.becker.freelance.app.backtest;

import javax.swing.*;

public class StrategyParameterConverter {

    public static void main(String[] args) {
        String strategyName = JOptionPane.showInputDialog("Strategy-Name");
        String pair = JOptionPane.showInputDialog("Pair");
        String parameters = JOptionPane.showInputDialog("Parameters");


        String[] split = parameters.split("}");
        for (String parameterWithRegime : split) {
            System.out.println(transform(strategyName, pair, parameterWithRegime));
        }

    }

    private static String transform(String strategyName, String pair, String parameterWithRegime) {
        String[] split = parameterWithRegime.split("\": ");

        return String.format("""
                {
                "strategyName": "%s",
                "priority": 100,
                "pair": "%s",
                "regimes": [%s"],
                "parameters": %s}
                },
                """, strategyName.trim(), pair.trim(), split[0].trim(), split[1].trim());
    }
}
