package com.becker.freelance.app.backtest;

import com.becker.freelance.strategies.creation.StrategyCreator;

import java.util.Comparator;

public class AllStrategyPrinter {

    public static void main(String[] args) {
        StrategyCreator.findAll().stream()
                .sorted(Comparator.comparing(StrategyCreator::strategyName))
                .forEach(creator -> System.out.println("\"" + creator.strategyName() + "\","));
    }
}
