from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def save_net_pnl_heatmap(
    results_df: pd.DataFrame,
    output_path: str | Path,
) -> None:
    if results_df.empty:
        return

    pivot = results_df.pivot_table(
        index="entry_delay_min",
        columns="min_gap_pct",
        values="net_pnl",
        aggfunc="mean",
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(pivot.values, aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([str(x) for x in pivot.columns])

    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels([str(y) for y in pivot.index])

    ax.set_xlabel("min_gap_pct")
    ax.set_ylabel("entry_delay_min")
    ax.set_title("Gap Fill Sweep Heatmap (Net PnL)")

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            if pd.notna(value):
                ax.text(j, i, f"{value:.2f}", ha="center", va="center")

    fig.colorbar(im, ax=ax, label="Net PnL")
    fig.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)