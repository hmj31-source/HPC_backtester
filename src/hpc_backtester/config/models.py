from dataclasses import dataclass
from typing import Any

@dataclass
class BacktestConfig:
    initial_capital: float 
    commission_pershare: float
    slippage_bps: float
    timeframe:str
    start_date: str
    end_date: str
    symbols: list[str]
    data_path: str

@dataclass  
class StrategyConfig:
    name: str
    params: dict[str, any]

@dataclass  
class RuntimeConfig:
    save_results: bool
    results_dir: str

@dataclass
class AppConfig:
    project_name: str
    backtest: BacktestConfig
    strategy: StrategyConfig
    runtime: RuntimeConfig