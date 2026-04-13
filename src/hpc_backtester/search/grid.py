import pandas as pd


def rank_results(results_df: pd.DataFrame) -> pd.DataFrame:
    if results_df.empty:
        return results_df
    
    ranked = results_df.copy()
    ranked["has_trades"] = ranked["num_trades"] > 0

    ranked = ranked.sort_values(
        by=["has_trades", "net_pnl", "expectancy", "win_rate"],
        ascending=[False, False, False, False],
    ).reset_index(drop = True)

    ranked = ranked.drop(columns=["has_trades"])

    return ranked