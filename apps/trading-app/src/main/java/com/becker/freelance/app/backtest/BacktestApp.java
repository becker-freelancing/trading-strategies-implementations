package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractBacktestAppBuilder;
import com.becker.freelance.math.Decimal;

import java.time.LocalDateTime;

public class BacktestApp {

    public static void main(String[] args) {
        Runnable backtestApp = AbstractBacktestAppBuilder.builder()
                .withInitialWalletAmount(new Decimal(200_000))
                .withFromTime(LocalDateTime.parse("2023-01-01T00:00:00"))
                .withToTime(LocalDateTime.parse("2023-05-01T00:00:00"))
                .build();

        backtestApp.run();
    }
}
