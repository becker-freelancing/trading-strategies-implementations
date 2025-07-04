package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractLocalBacktestAppBuilder;
import com.becker.freelance.math.Decimal;

import java.time.LocalDateTime;

public class AiDataBacktestApp {

    public static void main(String[] args) {
        Runnable backtestApp = AbstractLocalBacktestAppBuilder.builder()
                .withInitialWalletAmount(new Decimal(5_000))
                .withFromTime(LocalDateTime.parse("2022-08-06T12:00:00"))
                .withToTime(LocalDateTime.parse("2024-04-30T23:59:00"))
//                .withFromTime(LocalDateTime.parse("2024-05-01T00:00:00"))
//                .withToTime(LocalDateTime.parse("2024-09-30T23:59:00"))
                .withStrategyConfig()
                .build();

        backtestApp.run();
    }
}
