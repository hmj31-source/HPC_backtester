from pathlib import Path
import json
from datetime import datetime
import pandas as pd

def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_run_summary(results: dict, results_dir: str, run_id: str) -> Path:
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"run_{run_id}.json"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    return json_path

def save_trades(trades_df: pd.DataFrame, results_dir: str, run_id: str) -> Path:
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / f"trades_{run_id}.csv"
    trades_df.to_csv(csv_path, index=False)

    return csv_path