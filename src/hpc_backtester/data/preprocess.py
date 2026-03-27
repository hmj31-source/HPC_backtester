import pandas as pd


def preprocess_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # enforce types
    df["symbol"] = df["symbol"].astype(str)

    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # drop bad rows
    df = df.dropna(subset=["timestamp", "symbol", "open", "high", "low", "close", "volume"])

    # sort
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    return df