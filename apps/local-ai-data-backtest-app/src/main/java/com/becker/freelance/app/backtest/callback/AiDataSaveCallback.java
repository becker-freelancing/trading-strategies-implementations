package com.becker.freelance.app.backtest.callback;

import com.becker.freelance.backtest.configuration.BacktestExecutionConfiguration;
import com.becker.freelance.backtest.util.FileUtil;
import com.becker.freelance.backtest.util.PathUtil;
import com.becker.freelance.commons.app.AppConfiguration;
import com.becker.freelance.commons.trade.Trade;
import com.becker.freelance.execution.callback.backtest.BacktestFinishedCallback;
import com.becker.freelance.strategies.creation.StrategyCreationParameter;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.List;

public class AiDataSaveCallback implements BacktestFinishedCallback {

    private String basePath = null;

    @Override
    public void initiate(AppConfiguration appConfiguration, BacktestExecutionConfiguration backtestExecutionConfiguration, String strategyName) {
        basePath = PathUtil.fromRelativePath("ai-data/" + strategyName + "/" + strategyName + ".csv");
    }

    @Override
    public void accept(List<Trade> trades, StrategyCreationParameter strategyCreationParameter) {
        Path writePath = Path.of(basePath);
        try {
            FileUtil.createIfNotExists(writePath);
            Files.writeString(writePath, "openTime;closeTime;pair;profitInEurosWithFees;openLevel;closeLevel;openFee;closeFee;size;direction;conversionRate;positionBehaviour;openMarketRegime\n");
        } catch (IOException e) {
            throw new IllegalStateException("Could not create file " + writePath, e);
        }

        for (Trade trade : trades) {
            try {
                Files.writeString(writePath,
                        String.format("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n",
                                trade.getOpenTime(),
                                trade.getCloseTime(),
                                trade.getPair(),
                                trade.getProfitInEuroWithFees(),
                                trade.getOpenLevel(),
                                trade.getCloseLevel(),
                                trade.getOpenFee(),
                                trade.getCloseFee(),
                                trade.getSize(),
                                trade.getDirection(),
                                trade.getConversionRate(),
                                trade.getPositionType(),
                                trade.getOpenMarketRegime()),
                        StandardCharsets.UTF_8, StandardOpenOption.APPEND);
            } catch (IOException e) {
                throw new IllegalStateException("Could not write trades to file " + writePath, e);
            }
        }

    }
}
