#!/bin/bash


java -cp app.jar:libs/* com.becker.freelance.app.backtest.RemoteBacktestApp &

python python/japy_starter.py