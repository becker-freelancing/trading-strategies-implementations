package com.becker.freelance.app.remote;

import com.becker.freelance.app.AbstractRemoteBacktestAppBuilder;

public class RemoteExecutionApp {

    public static void main(String[] args) {
        Runnable remoteBacktestApp = new AbstractRemoteBacktestAppBuilder().build();

        remoteBacktestApp.run();
    }
}
