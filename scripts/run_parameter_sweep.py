from pathlib import Path
import argparse
import logging
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from hpc_backtester.config.loader import load_config
from hpc_backtester.data.loader import load_ohlcv_csv
from hpc_backtester.parallel.multiprocessing_runner import run_sweep_multiprocessing
from hpc_backtester.search.parameter_space import build_gap_fill_param_space
from hpc_backtester.search.grid import rank_results
from hpc_backtester.storage.run_store import get_timestamp
from hpc_backtester.utils.logging import setup_logging


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

    logger.info("Generated %d parameter sets", len(param_sets))

    all_results = run_sweep_multiprocessing(
        df = df,
        strategy_name = config.strategy.name,
        param_sets= param_sets,
        initial_capital = config.backtest.initial_capital,
        commission_per_share= config.backtest.commission_per_share,
        slippage_bps = config.backtest.slippage_bps,
        n_workers= config.runtime.n_workers
    )

    results_df = pd.DataFrame(all_results)
    ranked_df = rank_results(results_df)

    logger.info("Sweep results:\n%s", ranked_df.to_string(index=False))

    if config.runtime.save_results:
        run_id = get_timestamp()
        out_dir = Path(config.runtime.results_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / f"sweep_gap_fill_{run_id}.csv"
        ranked_df.to_csv(out_path, index=False)
        logger.info("Saved sweep results to %s", out_path)

    logger.info("Sweep complete")


if __name__ == "__main__":
    main()