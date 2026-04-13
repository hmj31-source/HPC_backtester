def build_gap_fill_param_space(strategy_params: dict) -> list[dict]:
    min_gap_values = strategy_params.get("min_gap_pct_values", [0.02])
    entry_delay_values = strategy_params.get("entry_delay_min_vaues", [5])

    param_sets = []
    for min_gap_pct in min_gap_values:
        for entry_delay_min in entry_delay_values:
            param_sets.append(
                {
                    "min_gap_pct": float(min_gap_pct),
                    "entry_delay_min": int(entry_delay_min),
                    "target_fill_pct": strategy_params.get("target_fill_pct", 0.5),
                    "stop_atr_mult": strategy_params.get("stop_atr_mult", 1.0),
                }
            )

    return param_sets