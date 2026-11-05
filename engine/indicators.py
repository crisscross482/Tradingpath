"""SMC (Smart Money Concepts) & Technical Indicators Engine.

Implements:
- Exponential Moving Average (EMA) and Simple Moving Average (SMA)
- Average True Range (ATR)
- Dynamic Trend Ribbon (Fast MA, Slow MA, Trend MA)
- Fair Value Gaps (Bullish & Bearish FVG)
- Market Structure Pivots, Break of Structure (BOS), and Change of Character (CHOCH)
"""

from typing import List, Dict, Any, Optional
import math


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Calculate Exponential Moving Average."""
    if not prices or period <= 0:
        return []
    ema = []
    multiplier = 2 / (period + 1)

    # Initialize with SMA for the first valid period window
    if len(prices) < period:
        # Not enough data for full EMA, return SMA progression
        avg = sum(prices) / len(prices)
        return [avg] * len(prices)

    sma_first = sum(prices[:period]) / period
    for i in range(period - 1):
        ema.append(prices[i])  # placeholder until period is reached
    ema.append(sma_first)

    for i in range(period, len(prices)):
        val = (prices[i] - ema[-1]) * multiplier + ema[-1]
        ema.append(val)
    return ema


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> List[float]:
    """Calculate Average True Range (Wilder's RMA)."""
    n = len(closes)
    if n == 0 or len(highs) != n or len(lows) != n:
        return []

    tr = [highs[0] - lows[0]]
    for i in range(1, n):
        tr_val = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )
        tr.append(tr_val)

    # Wilder's Smoothing / RMA of TR
    atr = []
    if n < period:
        avg = sum(tr) / n
        return [avg] * n

    first_atr = sum(tr[:period]) / period
    for i in range(period - 1):
        atr.append(tr[i])
    atr.append(first_atr)

    for i in range(period, n):
        val = (atr[-1] * (period - 1) + tr[i]) / period
        atr.append(val)
    return atr


def detect_fair_value_gaps(
    highs: List[float],
    lows: List[float],
    min_size: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Detect Fair Value Gaps (FVG) in 3-candle patterns:
    - Bullish FVG: Low of candle[i] > High of candle[i-2]
    - Bearish FVG: High of candle[i] < Low of candle[i-2]
    """
    fvgs = []
    n = len(highs)
    if n < 3:
        return fvgs

    for i in range(2, n):
        # Bullish FVG
        if lows[i] > highs[i - 2]:
            gap_size = lows[i] - highs[i - 2]
            if gap_size >= min_size:
                fvgs.append({
                    "index": i,
                    "type": "bullish",
                    "top": lows[i],
                    "bottom": highs[i - 2],
                    "size": round(gap_size, 4)
                })
        # Bearish FVG
        elif highs[i] < lows[i - 2]:
            gap_size = lows[i - 2] - highs[i]
            if gap_size >= min_size:
                fvgs.append({
                    "index": i,
                    "type": "bearish",
                    "top": lows[i - 2],
                    "bottom": highs[i],
                    "size": round(gap_size, 4)
                })
    return fvgs


def detect_market_structure(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    pivot_len: int = 5
) -> List[Dict[str, Any]]:
    """
    Detect Break of Structure (BOS) and Change of Character (CHOCH)
    using swing pivot highs and lows.
    """
    n = len(closes)
    events = []
    if n < (pivot_len * 2 + 1):
        return events

    last_pivot_high = None
    last_pivot_low = None
    market_bias = 0  # 1: Bullish, -1: Bearish

    for i in range(pivot_len, n - pivot_len):
        current_high = highs[i]
        current_low = lows[i]

        # Check Pivot High
        is_ph = True
        for j in range(i - pivot_len, i + pivot_len + 1):
            if j != i and highs[j] >= current_high:
                is_ph = False
                break
        if is_ph:
            last_pivot_high = current_high

        # Check Pivot Low
        is_pl = True
        for j in range(i - pivot_len, i + pivot_len + 1):
            if j != i and lows[j] <= current_low:
                is_pl = False
                break
        if is_pl:
            last_pivot_low = current_low

        # Detect BOS / CHOCH on bar i + pivot_len
        check_idx = i + pivot_len
        if check_idx < n:
            close_val = closes[check_idx]
            if last_pivot_high is not None and close_val > last_pivot_high:
                structure_type = "CHOCH" if market_bias == -1 else "BOS"
                events.append({
                    "index": check_idx,
                    "type": structure_type,
                    "direction": "bullish",
                    "level": last_pivot_high
                })
                market_bias = 1

            if last_pivot_low is not None and close_val < last_pivot_low:
                structure_type = "CHOCH" if market_bias == 1 else "BOS"
                events.append({
                    "index": check_idx,
                    "type": structure_type,
                    "direction": "bearish",
                    "level": last_pivot_low
                })
                market_bias = -1

    return events


def compute_trend_ribbon(
    closes: List[float],
    fast_period: int = 10,
    slow_period: int = 30,
    trend_period: int = 200
) -> Dict[str, List[float]]:
    """Compute fast ribbon, slow ribbon, and major trend filter."""
    return {
        "fast_ma": calculate_ema(closes, fast_period),
        "slow_ma": calculate_ema(closes, slow_period),
        "trend_ma": calculate_ema(closes, trend_period)
    }
