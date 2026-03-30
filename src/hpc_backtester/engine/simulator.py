import logging
import pandas as pd

logger = logging.getLogger(__name__)

def apply_slippage(price: float, side: str, slippage_bps: float, is_entry: bool) -> float:
    slip = slippage_bps / 10000.0

    if side == "LONG":
        return price * (1 + slip) if is_entry else price * (1-slip)
    elif side == "SHORT":
        return price * (1 - slip) if is_entry else price * (1 + slip)
    
    return price

def run_backtest(df: pd.DataFrame, initial_capital: float, commission_per_share: float, slippage_bps: float,) -> dict:
    logger.info("Running simple signal-based backtest")

    trades = []
    capital = float(initial_capital)

    #one trade per signal row, exit as last bar of same sybmol/day
    signal_rows = df[df["entry_signal"]].copy()

    for _, signal_row in signal_rows.iterrows():
        symbol = signal_row["symbol"]
        trade_date =signal_row["trade_date"]
        entry_time = signal_row["timestamp"]
        raw_entry_price = float(signal_row["open"])

        day_slice = df[
            (df["symbol"] == symbol) &
            (df["trade_date"] == trade_date)
        ].copy()

        if day_slice.empty:
            continue
        
        exit_row = day_slice.iloc[-1]
        exit_time = exit_row["timestamp"]
        raw_exit_price = float(exit_row["close"])

        if bool(signal_row["long_entry"]):
            side = "LONG"
        elif bool(signal_row["short_entry"]):
            side = "SHORT"
        else:
            continue

        entry_price = apply_slippage(raw_entry_price, side, slippage_bps, is_entry=True)
        exit_price = apply_slippage(raw_exit_price, side, slippage_bps, is_entry=False)

        shares = 1
        gross_pnl = (exit_price - entry_price) if side == "LONG" else (entry_price - exit_price)
        total_commission = 2 * commission_per_share * shares
        net_pnl = gross_pnl - total_commission

        capital += net_pnl

        trades.append(
            {
                "symbol": symbol,
                "trade_date": str(trade_date),
                "side": side,
                "entry_time": str(entry_time),
                "entry_price": entry_price,
                "exit_time": str(exit_time),
                "exit_price": exit_price,
                "shares": shares,
                "gross_pnl": round(gross_pnl ,4),
                "commission": round(total_commission, 4),
                "net_pnl": round(net_pnl, 4),
                "win": net_pnl,
            }
        )

    trades_df = pd.DataFrame(trades)

    if trades_df.empty:
        results = {
            "inital_capital": float(initial_capital),
            "ending_capital": float(initial_capital),
            "net_pnl": 0.0,
            "num_trades": 0,
            "win_rate": 0.0,
            "avg_trade_pnl": 0.0,
            "gross_pnl": 0.0,
            "total_commission": 0.0,
        }
    else:
        gross_pnl_total = float(trades_df["gross_pnl"].sum())
        commission_total = float(trades_df["commission"].sum())
        net_pnl_total = float(trades_df["net_pnl"].sum())
        win_rate = float(trades_df["win"].mean()) * 100.0
        avg_trade_pnl = float(trades_df["net_pnl"].mean())
        results = {
            "inital_capital": round(float(initial_capital), 2),
            "ending_capital": round(float(capital), 2),
            "net_pnl": round(net_pnl_total, 2),
            "num_trades": int(len(trades_df)),
            "win_rate": round(win_rate, 2),
            "avg_trade_pnl": round(avg_trade_pnl, 4),
            "gross_pnl": round(gross_pnl_total, 4),
            "total_commission": round(commission_total, 4),
        }

    logger.info("Completed backtest with %d trades", results["num_trades"])

    return {
        "summary": results,
        "trades": trades_df,
    }