from pathlib import Path
import yaml

from hpc_backtester.config.models import(
    AppConfig,
    BacktestConfig,
    StrategyConfig,
    RuntimeConfig,
)

def load_config(path: str | Path) -> AppConfig:
    path = Path(path)

    with path.open("r", encoding="Utf-8") as f:
        raw = yaml.safe_load(f)

    return AppConfig(
        project_name=raw["project"]["name"],
        backtest=BacktestConfig(**raw["backtest"]),
        strategy=StrategyConfig(**raw["strategy"]),
        runtime=RuntimeConfig(**raw["runtime"]),
    )