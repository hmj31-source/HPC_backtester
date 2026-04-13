from __future__ import annotations

from typing import Any
import pandas as pd

from hpc_backtester.engine.simulator import run_backtest
from hpc_backtester.strategies.registry import STRATEGY_REGISTRY

def run_single_sweep_job(
        df: pd.DataFrame,
        strategy_name: str,
        params: dict[str, Any],
        initial_capital: float,
        slippage_bps: float,
) -> dict[str, Any]:
    strategy = STRATEGY_REGISTRY[strategy_name]

    run_df = df.copy()
    run_df = strategy.prepare_features(run_df)
    run_df = strategy.generate_entries(run_df, params)

    backest_output = run_backtest(
        df=run_df,
        initial_capital=initial_capital,
        commission_per_share = commission_per_share, 
        slippage_bps=slippage_bps,
    )

    summary = backtest_output["summary"].copy()
    summary["strategy_name"] = strategy_name
    summary["min_gap_pct"] = params["min_gap_pct"]
    summary["entry_delay_min"] = params["entry_delay_min"]
    summary["target_fill_pct"] = params["target_fill_pct"]
    summary["stop_atr_mult"] = params["stop_atr_mult"]

    return summary
