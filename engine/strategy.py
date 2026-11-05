"""TradePros SMC Strategy Signal Generation Engine.

Generates actionable trading signals based on:
- Trend ribbon alignment / crossovers
- Trend pullbacks
- Major trend filtering (200 EMA)
- Confluence with Fair Value Gaps (FVG) and Market Structure
- Dynamic ATR Stop Loss and multi-target Take Profits (TP1, TP2, TP3)
"""

from typing import List, Dict, Any, Optional
from engine.indicators import (
    calculate_ema,
    calculate_atr,
    detect_fair_value_gaps,
    compute_trend_ribbon
)


class TradeSignal:
    def __init__(
        self,
        index: int,
        timestamp: Optional[str],
        signal_type: str,  # 'BUY' or 'SELL'
        entry_price: float,
        stop_loss: float,
        tp1: float,
        tp2: float,
        tp3: float,
        risk: float,
        reward_risk_ratio: float,
        reason: str
    ):
        self.index = index
        self.timestamp = timestamp
        self.signal_type = signal_type
        self.entry_price = round(entry_price, 2)
        self.stop_loss = round(stop_loss, 2)
        self.tp1 = round(tp1, 2)
        self.tp2 = round(tp2, 2)
        self.tp3 = round(tp3, 2)
        self.risk = round(risk, 2)
        self.reward_risk_ratio = round(reward_risk_ratio, 2)
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "signal": self.signal_type,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "tp1": self.tp1,
            "tp2": self.tp2,
            "tp3": self.tp3,
            "risk": self.risk,
            "rr_ratio": self.reward_risk_ratio,
            "reason": self.reason
        }


def generate_smc_signals(
    opens: List[float],
    highs: List[float],
    lows: List[float],
    closes: List[float],
    timestamps: Optional[List[str]] = None,
    fast_len: int = 10,
    slow_len: int = 30,
    trend_len: int = 200,
    atr_len: int = 14,
    sl_atr_mult: float = 1.5,
    tp1_mult: float = 1.0,
    tp2_mult: float = 2.0,
    tp3_mult: float = 3.0,
    filter_by_trend: bool = True
) -> List[TradeSignal]:
    """
    Generate trade signals based on TradePros SMC confluence rules.
    """
    n = len(closes)
    if n < max(slow_len, atr_len) + 2:
        return []

    ribbon = compute_trend_ribbon(closes, fast_len, slow_len, trend_len)
    fast_ma = ribbon["fast_ma"]
    slow_ma = ribbon["slow_ma"]
    trend_ma = ribbon["trend_ma"]
    atr = calculate_atr(highs, lows, closes, atr_len)
    fvgs = detect_fair_value_gaps(highs, lows)
    fvg_indices = {item["index"]: item for item in fvgs}

    signals: List[TradeSignal] = []
    last_signal_dir = 0  # 1 = BUY, -1 = SELL

    start_idx = max(slow_len, atr_len)
    for i in range(start_idx, n):
        ts = timestamps[i] if timestamps and i < len(timestamps) else None
        close = closes[i]
        open_val = opens[i]
        fast = fast_ma[i]
        slow = slow_ma[i]
        prev_fast = fast_ma[i - 1]
        prev_slow = slow_ma[i - 1]
        t_ma = trend_ma[i]
        atr_val = atr[i] if atr[i] > 0 else (highs[i] - lows[i]) or 1.0

        is_bull_trend = fast > slow and (not filter_by_trend or close > t_ma)
        is_bear_trend = fast < slow and (not filter_by_trend or close < t_ma)

        # Cross conditions
        bull_cross = prev_fast <= prev_slow and fast > slow
        bear_cross = prev_fast >= prev_slow and fast < slow

        # Pullback triggers
        bull_pullback = (
            is_bull_trend and
            lows[i - 1] <= fast and
            close > fast and
            close > open_val
        )
        bear_pullback = (
            is_bear_trend and
            highs[i - 1] >= fast and
            close < fast and
            close < open_val
        )

        has_bull_fvg = (i in fvg_indices and fvg_indices[i]["type"] == "bullish")
        has_bear_fvg = (i in fvg_indices and fvg_indices[i]["type"] == "bearish")

        # BUY trigger
        if (bull_cross or bull_pullback or (is_bull_trend and has_bull_fvg)) and is_bull_trend and last_signal_dir != 1:
            sl_dist = atr_val * sl_atr_mult
            sl = close - sl_dist
            tp1 = close + (sl_dist * tp1_mult)
            tp2 = close + (sl_dist * tp2_mult)
            tp3 = close + (sl_dist * tp3_mult)
            reason = "Bullish Ribbon Crossover" if bull_cross else ("Bullish SMC Pullback" if bull_pullback else "Bullish FVG Confluence")

            signals.append(TradeSignal(
                index=i,
                timestamp=ts,
                signal_type="BUY",
                entry_price=close,
                stop_loss=sl,
                tp1=tp1,
                tp2=tp2,
                tp3=tp3,
                risk=sl_dist,
                reward_risk_ratio=tp2_mult,
                reason=reason
            ))
            last_signal_dir = 1

        # SELL trigger
        elif (bear_cross or bear_pullback or (is_bear_trend and has_bear_fvg)) and is_bear_trend and last_signal_dir != -1:
            sl_dist = atr_val * sl_atr_mult
            sl = close + sl_dist
            tp1 = close - (sl_dist * tp1_mult)
            tp2 = close - (sl_dist * tp2_mult)
            tp3 = close - (sl_dist * tp3_mult)
            reason = "Bearish Ribbon Crossover" if bear_cross else ("Bearish SMC Pullback" if bear_pullback else "Bearish FVG Confluence")

            signals.append(TradeSignal(
                index=i,
                timestamp=ts,
                signal_type="SELL",
                entry_price=close,
                stop_loss=sl,
                tp1=tp1,
                tp2=tp2,
                tp3=tp3,
                risk=sl_dist,
                reward_risk_ratio=tp2_mult,
                reason=reason
            ))
            last_signal_dir = -1

    return signals
