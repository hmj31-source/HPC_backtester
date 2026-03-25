from pathlib import Path
import json
from datetime import datetime

def save_run_summary(results: dict, results_dir: str) -> Path:
    out_dir = Path(results_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"run_{timestamp}.json"
    
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return out_path