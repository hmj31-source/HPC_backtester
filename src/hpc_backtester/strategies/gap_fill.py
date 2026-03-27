import logging
import pandas as pd

from hpc_backtester.strategies.base import BaseStrategy

logger = logging.getLogger(__name__)


class GapFillStrategy(BaseStrategy):
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

        #daily open = first open of each symbol per day
        daily_open = (
            df.groupby(["symbol", "trade_date"], as_index=False)
            .first()[["symbol", "trade_date", "open"]]
            .rename(columns={"open": "session_open"})
        )

        #daily close
        daily_close = (
            df.groupby(["symbol", "trade_date"], as_index=False)
            .last()[["symbol", "trade_date", "close"]]
            .rename(columns={"close": "daily_close"})
        )

        #previous day close by symbol
        daily_close = daily_close.sort_values(["symbol", "trade_date"]).reset_index(drop=True)
        daily_close["prev_close"] = daily_close.groupby("symbol")["daily_close"].shift(1)

        daily_features = daily_open.merge(
            daily_close[["symbol", "trade_date", "prev_close"]],
            on=["symbol", "trade_date"],
            how="left",
        )

        daily_features["gap_pct"] = (
            (daily_features["session_open"] - daily_features["prev_close"])
            / daily_features["prev_close"]
        )

        df = df.merge(
            daily_features,
            on=["symbol", "trade_date"],
            how="left",
        )

        logger.info("Prepared gap-fill features")
        return df

    def generate_entries(self, df: pd.DataFrame, params: dict) -> pd.DataFrame:
        df = df.copy()
        
        min_gap_pct = float(params.get("min_gap_pct", 0.02))

        #only first bar of each symbol/day can trigger entry in this verison
        first_bar_mask = df.groupby(["symbol", "trade_date"]).cumcount() == 0

        df["long_entry"] = first_bar_mask & (df["gap_pct"] <= -min_gap_pct)
        df["short_entry"] = first_bar_mask & (df["gap_pct"] >= min_gap_pct)
        df["entry_signal"] = df["long_entry"] | df["short_entry"]

        logger.info(
            "Generated gap_fill signals: %d entries",
            int(df["entry_signal"].sum())
        )

        return df