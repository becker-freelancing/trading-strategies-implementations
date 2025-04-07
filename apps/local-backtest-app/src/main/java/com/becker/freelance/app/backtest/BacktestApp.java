package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractLocalBacktestAppBuilder;
import com.becker.freelance.math.Decimal;

import java.time.LocalDateTime;

public class BacktestApp {

    public static void main(String[] args) {
        Runnable backtestApp = AbstractLocalBacktestAppBuilder.builder()
                .withInitialWalletAmount(new Decimal(200_000))
                .withFromTime(LocalDateTime.parse("2025-03-30T00:00:00"))
                .withToTime(LocalDateTime.parse("2025-04-06T00:00:00"))
                .build();

        backtestApp.run();
    }
}
