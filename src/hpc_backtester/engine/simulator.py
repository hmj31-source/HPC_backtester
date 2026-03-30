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

def compute_max_drawdown(equity_curve: pd.DataFrame) -> float:
    if equity_curve.empty:
        return 0.0
    
    running_peak = equity_curve["equity"].cummax()
    drawdown = equity_curve["equity"] - running_peak
    max_drawdown = drawdown.min()
    
    return float(max_drawdown)

def run_backtest(
    df: pd.DataFrame, 
    initial_capital: float,
    commission_per_share: float, 
    slippage_bps: float,
) -> dict:
    logger.info("Running signal-based backtest with costs and metrics")

    trades = []
    equity_points = []
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
                "entry_price": round(entry_price,4),
                "exit_time": str(exit_time),
                "exit_price": round(exit_price,4),
                "shares": shares,
                "gross_pnl": round(gross_pnl ,4),
                "commission": round(total_commission, 4),
                "net_pnl": round(net_pnl, 4),
                "win": bool(net_pnl > 0),
            }
        )
        equity_points.append(
            {
                "timestamp": str(exit_time),
                "symbol": symbol,
                "equity": round(capital, 4),
            }
        )

    trades_df = pd.DataFrame(trades)
    equity_curve_df = pd.DataFrame(equity_points)

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
            "avg_winner": 0.0,
            "avg_loser": 0.0,
            "profit_factor": 0.0,
            "expectancy": 0.0,
            "max_drawdown": 0.0,
        }
    else:
        winners = trades_df[trades_df["net_pnl"] > 0]
        losers = trades_df[trades_df["net_pnl"] < 0]

        gross_pnl_total = float(trades_df["gross_pnl"].sum())
        commission_total = float(trades_df["commission"].sum())
        net_pnl_total = float(trades_df["net_pnl"].sum())
        win_rate = float(trades_df["win"].mean()) * 100.0
        avg_trade_pnl = float(trades_df["net_pnl"].mean())

        avg_winner = float(winners["net_pnl"].mean()) if not winners.empty else 0.0
        avg_loser = float(losers["net_pnl"].sum()) if not losers.empty else 0.0
        
        gross_profit = float(winners["net_pnl"].sum()) if not winners.empty else 0.0
        gross_loss_abs = abs(float(losers["net_pnl"].sum())) if not losers.empty else 0.0
        
        if gross_loss_abs > 0:
            profit_factor = gross_profit / gross_loss_abs
        else:
            profit_factor = 0.0

        win_prob = len(winners) / len(trades_df)
        loss_prob = len(losers) / len(trades_df)
        expectancy = (win_prob * avg_winner) + (loss_prob * avg_loser)

        max_drawdown = compute_max_drawdown(equity_curve_df)

        results = {
            "initial_capital": round(float(initial_capital), 2),
            "ending_capital": round(float(capital), 2),
            "net_pnl": round(net_pnl_total, 2),
            "num_trades": int(len(trades_df)),
            "win_rate": round(win_rate, 2),
            "avg_trade_pnl": round(avg_trade_pnl, 4),
            "gross_pnl": round(gross_pnl_total, 4),
            "total_commission": round(commission_total, 4),
            "avg_winner": round(avg_winner, 4),
            "avg_loser": round(avg_loser , 4),
            "expectancy": round(expectancy , 4),
            "max_drawdown": round(max_drawdown, 4),
        }

    logger.info("Completed backtest with %d trades", results["num_trades"])

    return {
        "summary": results,
        "trades": trades_df,
        "equity_curve": equity_curve_df,
    }