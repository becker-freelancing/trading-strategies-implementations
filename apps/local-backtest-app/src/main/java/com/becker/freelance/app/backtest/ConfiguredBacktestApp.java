package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractLocalBacktestAppBuilder;
import com.becker.freelance.math.Decimal;

import java.time.LocalDateTime;
import java.util.List;

public class ConfiguredBacktestApp {

    public static void main(String[] args) {
        List<String> strategyNames = List.of(
                "2_MA_Strategy_simple",
                "2_EMA_Strategy_simple"
        );
        for (String strategyName : strategyNames) {

            Runnable backtestApp = AbstractLocalBacktestAppBuilder.builder()
                    .withInitialWalletAmount(new Decimal(5_000))
                    .withFromTime(LocalDateTime.parse("2024-05-01T00:00:00"))
                    .withToTime(LocalDateTime.parse("2024-09-30T23:59:00"))
                    .withAppMode("BYBIT_LOCAL_DEMO")
                    .withNumberOfThreads(20)
                    .withPair("ETHPERP_1")
                    .withStrategyName(strategyName)
                    .build();

            backtestApp.run();
        }
    }
}
