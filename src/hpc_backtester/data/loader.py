import logging
from pathlib import Path
import pandas as pd

from hpc_backtester.data.preprocess import preprocess_ohlcv
from hpc_backtester.data.schemas import REQUIRED_OHLCV_COLUMNS

logger = logging.getLogger(__name__)


def load_ohlcv_csv(
    csv_path: str,
    symbols: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pd.DataFrame:
    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"OHLCV file not found: {path}")

    logger.info("Loading OHLCV data from %s", path)
    df = pd.read_csv(path)

    missing_cols = REQUIRED_OHLCV_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {sorted(missing_cols)}")

    df = preprocess_ohlcv(df)

    if symbols:
        if isinstance(symbols, str):
            symbols = [symbols]
        df = df[df["symbol"].isin(symbols)]

    if start_date:
        df = df[df["timestamp"] >= pd.to_datetime(start_date)]

    if end_date:
        df = df[df["timestamp"] <= pd.to_datetime(end_date)]

    df = df.reset_index(drop=True)

    logger.info("Loaded %d cleaned OHLCV rows", len(df))
    logger.info("Symbols in dataset: %s", sorted(df["symbol"].unique().tolist()))

    return df