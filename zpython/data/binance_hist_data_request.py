import os

import pandas as pd
import requests


def get_historical_klines(symbol: str, interval: str, start: str, end: str = None):
    """
    Ruft historische Marktdaten (Kline-Daten) von der Binance API ab.
    :param symbol: Das Handelspaar (z.B. "BTCUSDT").
    :param interval: Zeitintervall (z.B. "1m" für 1-Minuten-Kerzen).
    :param start: Startdatum im Format "YYYY-MM-DD HH:MM:SS".
    :param end: Optional, Enddatum im Format "YYYY-MM-DD HH:MM:SS".
    :return: Pandas DataFrame mit den Kline-Daten.
    """
    base_url = "https://api.binance.com/api/v3/klines"
    start_timestamp = int(start.to_pydatetime().timestamp() * 1000)
    end_timestamp = int(end.to_pydatetime().timestamp() * 1000) if end else None

    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_timestamp,
        "endTime": end_timestamp,
        "limit": 1000
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if "code" in data:
        raise Exception(f"Fehler bei der API-Anfrage: {data}")

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume",
        "number_of_trades", "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    df = df.astype({"open": "float", "high": "float", "low": "float", "close": "float", "volume": "float"})

    return df


if __name__ == "__main__":
    symbol = "BTCEUR"
    interval = "1m"
    bars = 990

    path = f"./{symbol}_1_raw.csv"

    if os.path.exists(path):
        data = pd.read_csv(path)
        data["open_time"] = pd.to_datetime(data["open_time"])
    else:
        data = pd.DataFrame({}, columns=[
            "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume",
            "number_of_trades", "taker_buy_base", "taker_buy_quote", "ignore"
        ])

    try:
        for i in range(1000):
            end = data["open_time"].min()
            if len(data) == 0:
                end = pd.to_datetime("2025-03-01 00:00:00")
            start = end - pd.Timedelta(minutes=bars)
            print(f"{i} - {start} to {end}")
            df = get_historical_klines(symbol, interval, start, end)
            data = pd.concat([data, df])
            if i % 50 == 0:
                data.to_csv(path, index=False)
    except Exception as e:
        print(e)

    data.to_csv(path, index=False)

    # df = get_historical_klines(symbol, interval, start_date, end_date)
    # print(df.head())
