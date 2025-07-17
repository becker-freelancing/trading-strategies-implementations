package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractLocalBacktestAppBuilder;
import com.becker.freelance.math.Decimal;

import java.time.LocalDateTime;
import java.util.List;

public class ConfiguredBacktestApp {

    public static void main(String[] args) {
        List<String> strategyNames = List.of(
                //"2_MA_Strategy",
                "3_Ma_Strategy",
                "Bollinger_Band_Bounce"
        );
        for (String strategyName : strategyNames) {

            Runnable backtestApp = AbstractLocalBacktestAppBuilder.builder()
                    .withInitialWalletAmount(new Decimal(5_000))
                    .withFromTime(LocalDateTime.parse("2024-05-01T00:00:00"))
                    .withToTime(LocalDateTime.parse("2024-09-30T23:59:00"))
                    .withAppMode("BYBIT_LOCAL_DEMO")
                    .withNumberOfThreads(16)
                    .withPair("ETHPERP_1")
                    .withStrategyName(strategyName)
                    .withParameterPermutationLimit(1000)
                    .build();

            try {
                backtestApp.run();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}
