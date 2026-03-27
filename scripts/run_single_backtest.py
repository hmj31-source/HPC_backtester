from pathlib import Path
import argparse
import logging
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from hpc_backtester.config.loader import load_config
from hpc_backtester.data.loader import load_ohlcv_csv
from hpc_backtester.engine.simulator import run_backtest
from hpc_backtester.storage.run_store import save_run_summary
from hpc_backtester.strategies.registry import STRATEGY_REGISTRY
from hpc_backtester.utils.logging import setup_logging

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config YAML")
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Loading config from %s", args.config)
    config = load_config(args.config)

    logger.info("Loading data")
    df = load_ohlcv_csv(
        csv_path=config.backtest.data_path,
        symbols=config.backtest.symbols,
        start_date=config.backtest.start_date,
        end_date=config.backtest.end_date,
    )

    logger.info("Loading strategy: %s", config.strategy.name)
    strategy = STRATEGY_REGISTRY[config.strategy.name]

    df = strategy.prepare_features(df)
    df = strategy.generate_entries(df, config.strategy.params)

    results = run_backtest(df, config.backtest.initial_capital)

    if config.runtime.save_results:
        out_path = save_run_summary(results, config.runtime.results_dir)
        logger.info("Saved run summary to %s", out_path)

    logger.info("Finished successfully")
    logger.info("Results: %s", results)


if __name__ == "__main__":
    main()