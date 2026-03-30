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
from hpc_backtester.storage.run_store import save_run_summary, save_trades, get_timestamp
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

    signal_preview = df.loc[
        df["entry_signal"],
        ["timestamp", "symbol", "session_open", "prev_close", "gap_pct", "long_entry", "short_entry"]
    ]
    
    logger.info("Signal preview:\n%s", signal_preview.to_string(index=False) if not signal_preview.empty else "No signals gemerated")

    backtest_output = run_backtest(
        df = df,
        initial_capital=config.backtest.initial_capital,
        commission_per_share=config.backtest.commission_per_share,
        slippage_bps=config.backtest.slippage_bps,
    )

    results = backtest_output["summary"]
    trades_df = backtest_output["trades"]

    if not trades_df.empty:
        logger.info("trade preview:\n%s", trades_df.to_string(index=False))
    else:
        logger.info("No trades generated")

    if config.runtime.save_results:
        run_id = get_timestamp()
        summary_path = save_run_summary(results, config.runtime.results_dir, run_id)
        trades_path = save_trades(trades_df, config.runtime.results_dir, run_id)

        logger.info("Saved run summary to %s", summary_path)
        logger.info("Saved trades to %s", trades_path)

    logger.info("Finished successfully")
    logger.info("Results: %s", results)


if __name__ == "__main__":
    main()