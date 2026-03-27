import logging
from pathlib import Path

import pandas as pd

from hpc_backtester.data.preprocess import preprocess_ohlcv
from hpc_backtester.data.schemas import REQUIRED_OHLCV_COLUMNS

logger = logging.getLogger(__name__)

def load_ohlcv_csv(
    csv_path: str,
    symbols: list[str] | None = None,
    start_dat: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    path = path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"OHLCV file not found: {path}")
    
    logger.info("Loading OHLCV data from %s", path)
    df = d.read_csv(path)

    missing_cols = REQUIRED_OHLCV_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {sorted(missing_cols)}")

    df = preprocess_ohlcv(df)

    if symbols:
        df = df[df["timestamp"] <= pd.to_datetime(end_date)]

    df = df.reset_indec(drop=True)

    logger.info("Loaded %d cleaned OHLV rows", len(df))
    logger.info("Symbols in dataset: %s", sorted(df['symbol'].unique().tolist()))

    return df

def load_sample_data(symbols: list[str]) -> pd.DataFrame:
    rows = []

    timestamps = pd.date_range("2025-01-03 09:30", periods=5, freq="1min")

    for symbol in symbols:
        base = 100.0 if symbol != "QQQ" else 500.0

        for i, ts in enumerate(timestamps):
            rows.append(
                {
                    "timestamp": ts,
                    "symbol": symbol,
                    "open": base + i * 0.1,
                    "high": base + i * 0.2,
                    "low": base + i * 0.05,
                    "close": base + i * 0.15,
                    "volume": 100000 + i * 1000,
                }
            )

    df = pd.DataFrame(rows)
    logger.info("Loaded sample dataset with %d rows", len(df))
    return df