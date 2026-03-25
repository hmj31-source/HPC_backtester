from pathlib import Path
import yaml

from hpc_backtester.config.models import(
    Appconfig,
    BacktestConfig,
    StrategyConfig,
    RuntimeConfig,
)

def load_config(path: str | Path) -> AppConfig:
    path = yaml.safe_load(f)

    return Appconfig(
        project_name=raw["project"]["name"],
        backtest=BacktestConfig(**raw["backtest"]),
        strategy=StrategyConfig(**raw["strategy"]),
        runtime=RuntimeConfig(**raw["runtime"]),
    )