package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractBacktestAppBuilder;

import java.io.IOException;
import java.time.LocalDateTime;

public class BacktestContinueApp {

    public static void main(String[] args) throws IOException {
        Runnable backtestApp = AbstractBacktestAppBuilder.builder()
                .continueMode()
                .build();

        backtestApp.run();
    }
}
