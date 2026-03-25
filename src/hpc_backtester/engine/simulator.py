import logging
import pandas as pd

logger = logging.getLogger(__name__)

def run_backtest(df: pd.DataFrame, initial_capital: float) -> dict:
    logger.info("Running placeholder bakctest")
    return {
        "inital_capital": initial_capital,
        "ending_capital": initial_capital,
        "net_pnl": 0.0,
        "num_trades": 0,
    }