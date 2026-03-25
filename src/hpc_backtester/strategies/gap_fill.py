import logging
import pandas as pd

from hpc_backtester.strategies.base import BaseStrategy

logger = logging.getLogger(__name__)

class GapFillStrategy(BaseStrategy):
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["gap_pct"] = 0.0
        return df
    
    def generate_entreis(self, df: pd.DataFrame, params: dict) -> pd.DataFrame:
        df = df.copy()
        df["entry_signal"] = False
        logger.info("Generated placeholder entry dignals for gap fill")
        return df
    
    