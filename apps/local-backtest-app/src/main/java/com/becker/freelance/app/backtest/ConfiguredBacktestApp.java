package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractLocalBacktestAppBuilder;
import com.becker.freelance.math.Decimal;

import java.time.LocalDateTime;
import java.util.List;

public class ConfiguredBacktestApp {

    public static void main(String[] args) {
        List<String> strategyNames = List.of(
                "2_EMA_Strategy_min_ATR",
                "2_EMA_Strategy_simple",
                "2_EMA_Strategy_with_RSI_filter",
                "2_EMA_Strategy_with_long_EMA_filter",
                "2_MA_Strategy",
                "2_MA_Strategy_simple",
                "3_Ma_Strategy",
                "Best_Hard_TP_and_SL",
                "Bollinger_Band_Bounce",
                "Bollinger_Band_Bounce_Min_Slope",
                "MACD_Scalping",
                "Parabolic_SAR",
                "Rsi_Overbought_Oversold",
                "swing_high_low",
                "chart_pattern",
                "freq_strategy",
                "super_trend",
                "voltan_expan_close_strategy"
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
