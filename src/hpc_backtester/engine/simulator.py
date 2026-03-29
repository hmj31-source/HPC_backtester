import logging
import pandas as pd

logger = logging.getLogger(__name__)


def run_backtest(df: pd.DataFrame, initial_capital: float) -> dict:
    logger.info("Running simple signal-based backtest")

    trades = []
    capital = float(initial_capital)

    #one trade per signal row, exit as last bar of same sybmol/day
    signal_rows = df[df["entry_signal"]].copy()

    for _, signal_row in signal_rows.iterrows():
        symbol = signal_row["symbol"]
        trade_date =signal_row["trade_date"]
        entry_time = signal_row["timestamp"]
        entry_price = float(signal_row["open"])

        day_slice = df[
            (df["symbol"] == symbol) &
            (df["trade_date"] == trade_date)
        ].copy()

        if day_slice.empty:
            continue
        
        exit_row = day_slice.iloc[-1]
        exit_time = exit_row["timestamp"]
        exit_price = float(exit_row["close"])

        if bool(signal_row["long_entry"]):
            side = "LONG"
            pnl = exit_price - entry_price
        elif bool(signal_row["short_entry"]):
            side = "SHORT"
            pnl = entry_price - exit_price
        else:
            continue

        capital += pnl

        trades.append(
            {
                "symbol": symbol,
                "trade_date": str(trade_date),
                "side": side,
                "entry_time": str(entry_time),
                "entry_price": entry_price,
                "exit_time": str(exit_time),
                "exit_price": exit_price,
                "pnl": pnl,
            }
        )

    trades_df = pd.DataFrame(trades)

    results = {
        "inital_capital": float(initial_capital),
        "ending_capital": float(capital),
        "net_pnl": float(capital - initial_capital),
        "num_trades": int(len(trades)),
    }

    logger.info("Completed backtest with %d trades", results["num_trades"])

    return {
        "summary": results,
        "trades": trades_df,
    }