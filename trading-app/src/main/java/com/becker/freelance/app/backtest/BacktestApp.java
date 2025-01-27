package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractBacktestApp;

import java.io.IOException;
import java.time.LocalDateTime;

public class BacktestApp {

    public static void main(String[] args) throws IOException {
        AbstractBacktestApp backtestApp = AbstractBacktestApp.builder()
                .withInitialWalletAmount(2000.)
                .withFromTime(LocalDateTime.parse("2023-01-01T00:00:00"))
                .withToTime(LocalDateTime.parse("2024-01-01T00:00:00"))
                .build();

        backtestApp.run();
    }
}
