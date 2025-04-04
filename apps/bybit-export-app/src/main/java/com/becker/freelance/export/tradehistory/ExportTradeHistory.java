package com.becker.freelance.export.tradehistory;

import com.bybit.api.client.config.BybitApiConfig;
import com.bybit.api.client.domain.CategoryType;
import com.bybit.api.client.domain.position.request.PositionDataRequest;
import com.bybit.api.client.restApi.BybitApiPositionRestClient;
import com.bybit.api.client.service.BybitApiClientFactory;

import java.time.LocalDateTime;
import java.time.ZoneId;

public class ExportTradeHistory {

    public static void main(String[] args) {

        long exportStart = LocalDateTime.parse("2025-04-04T07:50:00").toEpochSecond(ZoneId.systemDefault().getRules().getOffset(LocalDateTime.now()));
        long exportEnd = LocalDateTime.parse("2025-05-01T00:00:00").toEpochSecond(ZoneId.systemDefault().getRules().getOffset(LocalDateTime.now()));


        BybitApiPositionRestClient bybitApiPositionRestClient = BybitApiClientFactory
                .newInstance(System.getenv("API_KEY"), System.getenv("SECRET"), BybitApiConfig.TESTNET_DOMAIN)
                .newPositionRestClient();

        Object closePnlList = bybitApiPositionRestClient.getClosePnlList(PositionDataRequest.builder()
                .category(CategoryType.LINEAR)
                .startTime(exportStart)
                .endTime(exportEnd)
                .limit(100)
                .build()
        );

        System.out.println(closePnlList);
    }
}
