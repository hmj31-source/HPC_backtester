HPC Backtester (Work in Progress)

A modular, high-performance backtesting engine designed for systematic trading strategy research. This project focuses on scalable architecture, clean abstractions, and extensibility for future parallelization and real-time data integration.

Overview

This project implements the core infrastructure for a quantitative trading backtesting system. The current version establishes a complete end-to-end pipeline:

Configuration loading (YAML-based)
Data ingestion (currently synthetic sample data)
Strategy abstraction and registry system
Backtest engine (placeholder execution)
Results logging and persistence

This foundation is designed to support advanced strategies such as gap fills, mean reversion, and momentum-based systems.

Project Structure
hpc_backtester/
│
├── configs/                # YAML configuration files
├── scripts/                # Entry-point scripts
├── src/hpc_backtester/
│   ├── config/             # Config models + loader
│   ├── data/               # Data loading (sample for now)
│   ├── strategies/         # Strategy base + implementations
│   ├── engine/             # Backtesting logic
│   ├── parallel/           # (future) multiprocessing / HPC
│   ├── metrics/            # (future) performance metrics
│   ├── storage/            # (future) results persistence
│   └── utils/              # shared utilities
│
├── results/                # Output JSON runs
├── requirements.txt
└── README.md
Current Features (Day 1)
YAML-based configuration system
Strongly typed config via dataclasses
Strategy interface with abstract base class
Strategy registry for dynamic loading
Sample OHLCV data generator
End-to-end execution pipeline
JSON result export
Example Run

From project root:

python scripts/run_single_backtest.py --config configs/base.yaml

Example output:

Loading config...
Loading data...
Running strategy: gap_fill
Running backtest...
Finished successfully

Results are saved to:

results/run_<timestamp>.json
Example Config
project:
  name: hpc_backtester

backtest:
  initial_capital: 10000
  commission_per_share: 0.005
  slippage_bps: 1.0
  timeframe: "1min"
  start_date: "2025-01-01"
  end_date: "2025-03-31"
  symbols: [SPY, QQQ]

strategy:
  name: gap_fill
  params:
    min_gap_pct: 0.02

runtime:
  save_results: true
  results_dir: results
Design Goals
Modular and extensible architecture
Strategy-agnostic engine
Scalable to multi-core / distributed systems
Clean separation of concerns (data, strategy, execution)
Easy integration with real market data APIs
Next Steps (Day 2+)
Replace synthetic data with real OHLCV ingestion
Implement basic PnL calculation and trade tracking
Add position management (entries, exits, stops)
Introduce performance metrics (Sharpe, drawdown)
Add multi-symbol support with batching
Prepare for parallel execution
Tech Stack
Python 3.10+
Pandas
PyYAML
Status

Early development (Day 1 complete). Core pipeline is functional; trading logic and analytics are in progress.

## Status Update

### Day 1
- Set up project structure
- Added YAML config loading
- Created strategy abstraction and registry
- Built placeholder backtest pipeline
- Added JSON result saving

### Day 2
- Replaced synthetic data with real CSV-based OHLCV loading
- Added schema validation for required market data columns
- Added preprocessing for timestamp parsing, numeric conversion, and sorting
- Added symbol and date filtering from config
- Verified end-to-end execution using real file-based market data

### Day 3
- Expanded sample market data to multiple trading days
- Implemented gap-fill feature engineering
- Calculated previous close, session open, and gap percentage
- Added long/short entry signal generation for gap-fill strategy
- Logged signal previews for easier debugging and validation

### Day 4
- Implemented first real trade execution loop
- Converted entry signals into simulated long/short trades
- Added same-day end-of-day exits
- Computed per-trade and aggregate PnL
- Logged trade previews and summary performance metrics

### Day 5
- Added commission and slippage modeling
- Computed gross and net PnL per trade
- Added win rate and average trade PnL metrics
- Exported trades to CSV for analysis
- Improved result reporting with summary statistics

### Day 6
- Added equity curve generation and CSV export
- Computed average winner and average loser
- Added expectancy and max drawdown metrics
- Expanded summary reporting for strategy evaluation
- Improved post-run analysis outputs