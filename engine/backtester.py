"""Backtesting Simulation Engine for TradePros SMC Strategy.

Simulates trades bar-by-bar:
- Tracks entry, dynamic Stop Loss, and scaled Take Profit targets (TP1, TP2, TP3)
- Calculates standard quantitative performance metrics:
  - Total Trades, Win Rate
  - Total Return, Profit Factor
  - Max Drawdown
  - Average Trade PnL
"""

from typing import List, Dict, Any, Optional
import math
from engine.strategy import TradeSignal, generate_smc_signals


class BacktestTrade:
    def __init__(self, signal: TradeSignal):
        self.signal = signal
        self.entry_index = signal.index
        self.entry_price = signal.entry_price
        self.signal_type = signal.signal_type
        self.stop_loss = signal.stop_loss
        self.tp1 = signal.tp1
        self.tp2 = signal.tp2
        self.tp3 = signal.tp3

        self.tp1_hit = False
        self.tp2_hit = False
        self.tp3_hit = False
        self.sl_hit = False
        self.exit_index: Optional[int] = None
        self.exit_price: Optional[float] = None
        self.pnl_points: float = 0.0
        self.status = "OPEN"  # 'OPEN', 'CLOSED_PROFIT', 'CLOSED_LOSS', 'CLOSED_PARTIAL'


def run_backtest(
    opens: List[float],
    highs: List[float],
    lows: List[float],
    closes: List[float],
    timestamps: Optional[List[str]] = None,
    tp1_qty_pct: float = 0.333,
    tp2_qty_pct: float = 0.333,
    tp3_qty_pct: float = 0.334,
    **strategy_kwargs
) -> Dict[str, Any]:
    """
    Executes a sequential bar-by-bar backtest of the SMC strategy signals.
    """
    signals = generate_smc_signals(
        opens=opens,
        highs=highs,
        lows=lows,
        closes=closes,
        timestamps=timestamps,
        **strategy_kwargs
    )

    n = len(closes)
    trades: List[BacktestTrade] = []
    active_trade: Optional[BacktestTrade] = None
    signal_map = {sig.index: sig for sig in signals}

    for i in range(n):
        # 1. Manage Active Trade
        if active_trade is not None:
            high = highs[i]
            low = lows[i]

            if active_trade.signal_type == "BUY":
                # Check Stop Loss first (conservative risk approach)
                if low <= active_trade.stop_loss:
                    active_trade.sl_hit = True
                    active_trade.exit_index = i
                    active_trade.exit_price = active_trade.stop_loss
                    # If TP1 was already taken, remaining size hits SL
                    remaining_pct = 1.0 - (tp1_qty_pct if active_trade.tp1_hit else 0.0) - (tp2_qty_pct if active_trade.tp2_hit else 0.0)
                    loss_pts = (active_trade.stop_loss - active_trade.entry_price) * remaining_pct
                    active_trade.pnl_points += loss_pts
                    active_trade.status = "CLOSED_PROFIT" if active_trade.pnl_points > 0 else "CLOSED_LOSS"
                    trades.append(active_trade)
                    active_trade = None
                else:
                    # Check TP1
                    if not active_trade.tp1_hit and high >= active_trade.tp1:
                        active_trade.tp1_hit = True
                        active_trade.pnl_points += (active_trade.tp1 - active_trade.entry_price) * tp1_qty_pct
                    # Check TP2
                    if not active_trade.tp2_hit and high >= active_trade.tp2:
                        active_trade.tp2_hit = True
                        active_trade.pnl_points += (active_trade.tp2 - active_trade.entry_price) * tp2_qty_pct
                    # Check TP3 (Full exit)
                    if high >= active_trade.tp3:
                        active_trade.tp3_hit = True
                        active_trade.exit_index = i
                        active_trade.exit_price = active_trade.tp3
                        active_trade.pnl_points += (active_trade.tp3 - active_trade.entry_price) * tp3_qty_pct
                        active_trade.status = "CLOSED_PROFIT"
                        trades.append(active_trade)
                        active_trade = None

            elif active_trade.signal_type == "SELL":
                # Check Stop Loss first
                if high >= active_trade.stop_loss:
                    active_trade.sl_hit = True
                    active_trade.exit_index = i
                    active_trade.exit_price = active_trade.stop_loss
                    remaining_pct = 1.0 - (tp1_qty_pct if active_trade.tp1_hit else 0.0) - (tp2_qty_pct if active_trade.tp2_hit else 0.0)
                    loss_pts = (active_trade.entry_price - active_trade.stop_loss) * remaining_pct
                    active_trade.pnl_points += loss_pts
                    active_trade.status = "CLOSED_PROFIT" if active_trade.pnl_points > 0 else "CLOSED_LOSS"
                    trades.append(active_trade)
                    active_trade = None
                else:
                    # Check TP1
                    if not active_trade.tp1_hit and low <= active_trade.tp1:
                        active_trade.tp1_hit = True
                        active_trade.pnl_points += (active_trade.entry_price - active_trade.tp1) * tp1_qty_pct
                    # Check TP2
                    if not active_trade.tp2_hit and low <= active_trade.tp2:
                        active_trade.tp2_hit = True
                        active_trade.pnl_points += (active_trade.entry_price - active_trade.tp2) * tp2_qty_pct
                    # Check TP3 (Full exit)
                    if low <= active_trade.tp3:
                        active_trade.tp3_hit = True
                        active_trade.exit_index = i
                        active_trade.exit_price = active_trade.tp3
                        active_trade.pnl_points += (active_trade.entry_price - active_trade.tp3) * tp3_qty_pct
                        active_trade.status = "CLOSED_PROFIT"
                        trades.append(active_trade)
                        active_trade = None

        # 2. Enter new trade if signal exists and no active trade
        if active_trade is None and i in signal_map:
            active_trade = BacktestTrade(signal_map[i])

    # If trade still open at end of data, calculate mark-to-market
    if active_trade is not None:
        last_close = closes[-1]
        active_trade.exit_index = n - 1
        active_trade.exit_price = last_close
        remaining_pct = 1.0 - (tp1_qty_pct if active_trade.tp1_hit else 0.0) - (tp2_qty_pct if active_trade.tp2_hit else 0.0)
        diff = (last_close - active_trade.entry_price) if active_trade.signal_type == "BUY" else (active_trade.entry_price - last_close)
        active_trade.pnl_points += diff * remaining_pct
        active_trade.status = "CLOSED_PROFIT" if active_trade.pnl_points > 0 else "CLOSED_LOSS"
        trades.append(active_trade)

    # 3. Compute Metrics
    total_trades = len(trades)
    winning_trades = [t for t in trades if t.pnl_points > 0]
    losing_trades = [t for t in trades if t.pnl_points < 0]

    win_count = len(winning_trades)
    loss_count = len(losing_trades)
    win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0

    gross_profit = sum(t.pnl_points for t in winning_trades)
    gross_loss = abs(sum(t.pnl_points for t in losing_trades))
    net_pnl = gross_profit - gross_loss

    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 1.0)

    # Calculate Drawdown
    equity_curve = [0.0]
    peak = 0.0
    max_dd = 0.0
    curr_equity = 0.0

    for t in trades:
        curr_equity += t.pnl_points
        equity_curve.append(curr_equity)
        if curr_equity > peak:
            peak = curr_equity
        dd = peak - curr_equity
        if dd > max_dd:
            max_dd = dd

    return {
        "total_trades": total_trades,
        "winning_trades": win_count,
        "losing_trades": loss_count,
        "win_rate_percent": round(win_rate, 2),
        "gross_profit_points": round(gross_profit, 2),
        "gross_loss_points": round(gross_loss, 2),
        "net_pnl_points": round(net_pnl, 2),
        "profit_factor": round(profit_factor, 2),
        "max_drawdown_points": round(max_dd, 2),
        "trades": [
            {
                "entry_index": t.entry_index,
                "exit_index": t.exit_index,
                "signal": t.signal_type,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "pnl_points": round(t.pnl_points, 2),
                "tp1_hit": t.tp1_hit,
                "tp2_hit": t.tp2_hit,
                "tp3_hit": t.tp3_hit,
                "sl_hit": t.sl_hit,
                "status": t.status
            }
            for t in trades
        ]
    }
