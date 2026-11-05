"""Unit and Integration Tests for TradePros SMC Trading Indicator & Strategy.
"""

import pytest
from engine.indicators import (
    calculate_ema,
    calculate_atr,
    detect_fair_value_gaps,
    detect_market_structure,
    compute_trend_ribbon
)
from engine.strategy import TradeSignal, generate_smc_signals
from engine.backtester import run_backtest
from engine.alerts import parse_tradingview_alert, format_telegram_alert, format_discord_webhook


def test_calculate_ema():
    prices = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
    ema = calculate_ema(prices, period=3)
    assert len(ema) == len(prices)
    assert ema[2] == pytest.approx(11.0)
    assert ema[-1] > ema[0]


def test_calculate_atr():
    highs = [10.5, 11.5, 12.5, 13.5, 14.5]
    lows = [9.5, 10.0, 11.0, 12.0, 13.0]
    closes = [10.0, 11.0, 12.0, 13.0, 14.0]
    atr = calculate_atr(highs, lows, closes, period=3)
    assert len(atr) == len(closes)
    for val in atr:
        assert val > 0.0


def test_detect_fair_value_gaps():
    # Bullish FVG: low[2] > high[0]
    highs = [100.0, 105.0, 110.0]
    lows = [95.0, 102.0, 106.0]
    # Candle 2 low is 106.0, Candle 0 high is 100.0 => Gap of 6.0
    fvgs = detect_fair_value_gaps(highs, lows, min_size=1.0)
    assert len(fvgs) == 1
    assert fvgs[0]["type"] == "bullish"
    assert fvgs[0]["size"] == 6.0
    assert fvgs[0]["top"] == 106.0
    assert fvgs[0]["bottom"] == 100.0

    # Bearish FVG: high[2] < low[0]
    highs_bear = [100.0, 95.0, 92.0]
    lows_bear = [98.0, 93.0, 90.0]
    # Candle 2 high is 92.0, Candle 0 low is 98.0 => Gap of 6.0
    bear_fvgs = detect_fair_value_gaps(highs_bear, lows_bear, min_size=1.0)
    assert len(bear_fvgs) == 1
    assert bear_fvgs[0]["type"] == "bearish"
    assert bear_fvgs[0]["size"] == 6.0


def test_detect_market_structure():
    # Construct a swing high and subsequent break
    highs = [10.0, 12.0, 15.0, 12.0, 10.0, 11.0, 16.0, 14.0, 12.0]
    lows = [8.0, 10.0, 11.0, 10.0, 8.0, 9.0, 12.0, 11.0, 10.0]
    closes = [9.0, 11.0, 14.0, 11.0, 9.0, 10.0, 15.5, 13.0, 11.0]

    events = detect_market_structure(highs, lows, closes, pivot_len=2)
    assert isinstance(events, list)


def test_strategy_signal_generation():
    # Generate synthetic trending data
    n = 60
    opens = [2000.0 + i * 2.0 for i in range(n)]
    highs = [p + 3.0 for p in opens]
    lows = [p - 1.0 for p in opens]
    closes = [p + 2.0 for p in opens]

    signals = generate_smc_signals(
        opens=opens,
        highs=highs,
        lows=lows,
        closes=closes,
        fast_len=5,
        slow_len=15,
        trend_len=30,
        filter_by_trend=False
    )
    assert len(signals) > 0
    first_sig = signals[0]
    assert first_sig.signal_type in ("BUY", "SELL")
    assert first_sig.stop_loss > 0
    assert first_sig.tp1 > 0
    assert first_sig.tp2 > first_sig.tp1 if first_sig.signal_type == "BUY" else first_sig.tp2 < first_sig.tp1


def test_backtest_runner():
    n = 80
    opens = [2600.0 + i * 1.5 for i in range(n)]
    highs = [p + 4.0 for p in opens]
    lows = [p - 1.0 for p in opens]
    closes = [p + 3.0 for p in opens]

    results = run_backtest(
        opens=opens,
        highs=highs,
        lows=lows,
        closes=closes,
        fast_len=5,
        slow_len=15,
        trend_len=30,
        filter_by_trend=False
    )

    assert "total_trades" in results
    assert "win_rate_percent" in results
    assert "net_pnl_points" in results
    assert "trades" in results


def test_alert_parsing_and_formatting():
    # JSON payload
    json_alert = '{"ticker": "XAUUSD", "signal": "BUY", "price": 2740.50, "sl": 2728.00, "tp1": 2750.00, "tp2": 2760.00}'
    parsed_json = parse_tradingview_alert(json_alert)
    assert parsed_json["ticker"] == "XAUUSD"
    assert parsed_json["signal"] == "BUY"
    assert parsed_json["price"] == 2740.50
    assert parsed_json["sl"] == 2728.00

    # Text payload
    text_alert = "TradePros BUY Signal on XAUUSD at 2740.50 | SL: 2728.00"
    parsed_text = parse_tradingview_alert(text_alert)
    assert parsed_text["ticker"] == "XAUUSD"
    assert parsed_text["signal"] == "BUY"
    assert parsed_text["price"] == 2740.50
    assert parsed_text["sl"] == 2728.00

    # Telegram format
    tg_msg = format_telegram_alert(parsed_json)
    assert "TradePros SMC Signal Alert" in tg_msg
    assert "XAUUSD" in tg_msg
    assert "2740.50" in tg_msg

    # Discord format
    dc_msg = format_discord_webhook(parsed_json)
    assert "embeds" in dc_msg
    assert len(dc_msg["embeds"]) == 1
    assert dc_msg["embeds"][0]["title"] == "TradePros Alert: BUY XAUUSD"
