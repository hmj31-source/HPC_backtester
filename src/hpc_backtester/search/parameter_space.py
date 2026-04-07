def build_gap_fill_param_space(strategy_params: dict) -> list[dict]:
    min_gap_values = strategy_params.get("min_gap_pct_values", [0.02])

    param_sets = []
    for min_gap_pct in min_gap_values:
        param_sets.append(
            {
                "min_gap_pct": float(min_gap_pct),
                "entry_delay_min": strategy_params.get("entry_delay_min", 5),
                "target_fill_pct": strategy_params.get("target_fill_pct", 0.5),
                "stop_atr_mult": strategy_params.get("stop_atr_mult", 1.0),
            }
        )

    return param_sets