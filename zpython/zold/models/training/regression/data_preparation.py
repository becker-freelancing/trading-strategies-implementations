import pandas as pd


def get_reindex_freq(file_path):
    if "_5." in file_path or "_5_" in file_path:
        return "5min"

    if "_1." in file_path or "_1_" in file_path:
        return "1min"

    if "_15." in file_path or "_15_" in file_path:
        return "15min"

    if "_30." in file_path or "_30_" in file_path:
        return "30min"

    if "_60." in file_path or "_60_" in file_path:
        return "60min"

    if "_1440." in file_path or "_1440_" in file_path:
        return "1440min"



    raise Exception("get_reindex_freq not implemented for " + file_path)


def ffill(df, file_path):
    new_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq=get_reindex_freq(file_path))
    df = df.reindex(new_index)

    df["zero_group"] = (df['closeBid'].isna()).astype(int).groupby((df['closeBid'].notna()).cumsum()).cumsum()

    df["closeBid"] = df["closeBid"].ffill().where(df["zero_group"] < 15)
    df["highBid"] = df["highBid"].ffill()
    df["lowBid"] = df["lowBid"].ffill()
    df["openBid"] = df["openBid"].ffill()
    if "trades" in df.columns:
        df["trades"] = df["trades"].fillna(0)
        df["volume"] = df["volume"].fillna(0)
    else:
        df["trades"] = 0
        df["volume"] = 0
    if "-ig" in file_path or "-spread" in file_path or "-histdata" in file_path:
        df["closeAsk"] = df["closeAsk"].ffill()
        df["highAsk"] = df["highAsk"].ffill()
        df["lowAsk"] = df["lowAsk"].ffill()
        df["openAsk"] = df["openAsk"].ffill()

    df = df.dropna()
    df = df.drop("zero_group", axis=1)

    return df


def read_data(file_path) -> pd.DataFrame:
    print("Reading data...")
    df = pd.read_csv(file_path, compression="zip")
    df["closeTime"] = pd.to_datetime(df["closeTime"])
    df.set_index("closeTime", inplace=True)
    df = df.loc[~df.index.duplicated(keep='first')]
    print("Filling data...")
    df = ffill(df, file_path)
    return df
