package com.becker.freelance.app.backtest;

import com.becker.freelance.app.AbstractRemoteBacktestAppBuilder;

public class RemoteBacktestApp {

    public static void main(String[] args) {
        Runnable remoteBacktestApp = new AbstractRemoteBacktestAppBuilder().build();

        remoteBacktestApp.run();
    }
}
