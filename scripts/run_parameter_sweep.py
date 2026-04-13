from pathlib import Path
import argparse
import logging
import sys
import time
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from hpc_backtester.config.loader import load_config
from hpc_backtester.data.loader import load_ohlcv_csv
from hpc_backtester.parallel.multiprocessing_runner import run_sweep_multiprocessing
from hpc_backtester.parallel.worker import run_single_sweep_job
from hpc_backtester.search.parameter_space import build_gap_fill_param_space
from hpc_backtester.search.grid import rank_results
from hpc_backtester.storage.run_store import get_timestamp
from hpc_backtester.utils.logging import setup_logging
from hpc_backtester.visualization.heatmaps import save_net_pnl_heatmap


def run_sweep_sequential(
    df,
    strategy_name,
    param_sets,
    initial_capital,
    commission_per_share,
    slippage_bps,
):
    results = []
    for params in param_sets:
        summary = run_single_sweep_job(
            df=df,
            strategy_name=strategy_name,
            params=params,
            initial_capital=initial_capital,
            commission_per_share=commission_per_share,
            slippage_bps=slippage_bps,
        )
        results.append(summary)

    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to sweep config YAML")
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Loading sweep config from %s", args.config)
    config = load_config(args.config)

    logger.info("Loading OHLCV data once for sweep")
    df = load_ohlcv_csv(
        csv_path=config.backtest.data_path,
        symbols=config.backtest.symbols,
        start_date=config.backtest.start_date,
        end_date=config.backtest.end_date,
    )

    param_sets = build_gap_fill_param_space(config.strategy.params)
    logger.info("Generated %d parameter sets", len(param_sets))
    logger.info("Running sweep with %d worker(s)", config.runtime.n_workers)

    seq_start = time.perf_counter()
    sequential_results = run_sweep_sequential(
        df=df,
        strategy_name=config.strategy.name,
        param_sets=param_sets,
        initial_capital=config.backtest.initial_capital,
        commission_per_share=config.backtest.commission_per_share,
        slippage_bps=config.backtest.slippage_bps,
    )
    seq_elapsed = time.perf_counter() - seq_start

    par_start = time.perf_counter()
    parallel_results = run_sweep_multiprocessing(
        df=df,
        strategy_name=config.strategy.name,
        param_sets=param_sets,
        initial_capital=config.backtest.initial_capital,
        commission_per_share=config.backtest.commission_per_share,
        slippage_bps=config.backtest.slippage_bps,
        n_workers=config.runtime.n_workers,
    )
    par_elapsed = time.perf_counter() - par_start

    results_df = pd.DataFrame(parallel_results)
    ranked_df = rank_results(results_df)

    sequential_df = pd.DataFrame(sequential_results)
    sequential_ranked_df = rank_results(sequential_df)

    same_shape = ranked_df.shape == sequential_ranked_df.shape
    same_columns = list(ranked_df.columns) == list(sequential_ranked_df.columns)
    same_values = ranked_df.equals(sequential_ranked_df)

    speedup = (seq_elapsed / par_elapsed) if par_elapsed > 0 else 0.0

    benchmark_summary = {
        "strategy_name": config.strategy.name,
        "num_parameter_sets": len(param_sets),
        "n_workers": config.runtime.n_workers,
        "sequential_runtime_sec": round(seq_elapsed, 6),
        "parallel_runtime_sec": round(par_elapsed, 6),
        "speedup_factor": round(speedup, 4),
        "results_match": bool(same_shape and same_columns and same_values),
    }

    logger.info("Top sweep results:\n%s", ranked_df.head(10).to_string(index=False))
    logger.info("Benchmark summary: %s", benchmark_summary)

    if config.runtime.save_results:
        run_id = get_timestamp()
        out_dir = Path(config.runtime.results_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        sweep_path = out_dir / f"sweep_gap_fill_{run_id}.csv"
        benchmark_path = out_dir / f"benchmark_gap_fill_{run_id}.json"
        heatmap_path = out_dir / f"heatmap_gap_fill_{run_id}.png"

        ranked_df.to_csv(sweep_path, index=False)

        with benchmark_path.open("w", encoding="utf-8") as f:
            json.dump(benchmark_summary, f, indent=2)

        save_net_pnl_heatmap(ranked_df, heatmap_path)

        logger.info("Saved sweep results to %s", sweep_path)
        logger.info("Saved benchmark summary to %s", benchmark_path)
        logger.info("Saved heatmap to %s", heatmap_path)

    logger.info("Sweep complete")


if __name__ == "__main__":
    main()