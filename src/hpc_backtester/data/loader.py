import logging
import pandas as pd

logger = logging.getLogger(__name__)


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