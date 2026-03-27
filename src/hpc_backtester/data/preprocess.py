import pandas as pd

def preprocess_ohlv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["symbol"] = df["symbol"].astype(str)

    numeric_cols = ["open", "high", "low", "close", "volume"]
    for cols in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["timestamp", "symbol", "open", "high", "low", "close", "volume"])
    df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    return df