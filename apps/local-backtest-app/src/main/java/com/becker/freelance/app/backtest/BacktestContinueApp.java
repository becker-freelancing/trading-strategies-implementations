package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractLocalBacktestAppBuilder;

import java.io.IOException;

public class BacktestContinueApp {

    public static void main(String[] args) throws IOException {
        Runnable backtestApp = AbstractLocalBacktestAppBuilder.builder()
                .continueMode()
                .build();

        backtestApp.run();
    }
}
