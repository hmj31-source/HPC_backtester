from __future__ import annotations

from multiprocessing import Pool, cpu_count
from typing import Any
import pandas as pd

from hpc_backtester.parallel.worker import run_single_sweep_job

def _job_wrapper(job: dict[str, Any]) -> dict[str, Any]:
    return run_single_sweep_job(
        df = job["df"]
        strategy_name=job["strategy_name"],
        params= job["params"]
        initial_capital= job["initial_capital"],
        commission_per_share = job["commission_per_share"],
        slippage_bps= = job["slippage_bps"],
    )

def run_sweep_multiprocessing(
    df: pd.DataFrame,
    strategy_name: str,
    param_sets: list[dict[str, Any]],
    commission_per_share: float,
    slippage_bps: float,
    n_workers: int | None = None,
) -> list[dict[str, Any]]:
    if n_workers is None or n_workers < 1:
        n_wotkers = max(cpu_count() -1, 1)

    jobs = [
        {
            "df": df,
            "strategy_name": strategy_name,
            "params": params,
            "initial_capital": inital_capital,
            "commission_per_share": commission_per_share, 
            "slippage_bps": slippage_bps,
        }
        for params in param_sets
    ]
    
    with Pool(processes=n_workers) as pool:
        results = pool.map(_job_wrapper, jobs)

    return results