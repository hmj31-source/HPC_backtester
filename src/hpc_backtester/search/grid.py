import pandas as pd


def rank_results(results_df: pd.DataFrame) -> pd.DataFrame:
    if results_df.empty:
        return results_df

    return results_df.sort_values(
        by=["net_pnl", "win_rate", "expectancy"],
        ascending=[False, False, False]
    ).reset_index(drop=True)