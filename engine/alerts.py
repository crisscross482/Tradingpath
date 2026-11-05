"""TradingView Webhook & Signal Alert Dispatcher.

Parses incoming webhook JSON or text payloads and formats them for
Discord, Telegram, or automated execution bots.
"""

from typing import Dict, Any, Optional
import json
import re


def parse_tradingview_alert(raw_payload: str) -> Dict[str, Any]:
    """
    Parses a TradingView alert message.
    Supports either JSON string or structured text line format.
    """
    raw_payload = raw_payload.strip()

    # Try parsing as JSON first
    try:
        data = json.loads(raw_payload)
        if isinstance(data, dict):
            return {
                "ticker": data.get("ticker", "XAUUSD"),
                "signal": data.get("signal", data.get("action", "BUY")).upper(),
                "price": float(data.get("price", data.get("close", 0.0))),
                "sl": float(data.get("sl", data.get("stop_loss", 0.0))),
                "tp1": float(data.get("tp1", 0.0)),
                "tp2": float(data.get("tp2", 0.0)),
                "tp3": float(data.get("tp3", 0.0)),
                "comment": data.get("comment", "TradePros Alert")
            }
    except Exception:
        pass

    # Parse plain text format
    # Example: "TradePros BUY Signal on XAUUSD at 2735.50 | SL: 2725.00"
    signal_match = re.search(r"(BUY|SELL)", raw_payload, re.IGNORECASE)
    signal = signal_match.group(1).upper() if signal_match else "UNKNOWN"

    ticker_match = re.search(r"(?:on\s+)([A-Za-z0-9_]+)", raw_payload)
    ticker = ticker_match.group(1) if ticker_match else "XAUUSD"

    price_match = re.search(r"(?:at\s+)([0-9]+(?:\.[0-9]+)?)", raw_payload)
    price = float(price_match.group(1)) if price_match else 0.0

    sl_match = re.search(r"(?:SL:\s*)([0-9]+(?:\.[0-9]+)?)", raw_payload)
    sl = float(sl_match.group(1)) if sl_match else 0.0

    return {
        "ticker": ticker,
        "signal": signal,
        "price": price,
        "sl": sl,
        "tp1": 0.0,
        "tp2": 0.0,
        "tp3": 0.0,
        "comment": raw_payload
    }


def format_telegram_alert(alert_data: Dict[str, Any]) -> str:
    """Format structured alert into a clean Telegram Markdown message."""
    sig = alert_data.get("signal", "ALERT").upper()
    icon = "🟢" if sig == "BUY" else ("🔴" if sig == "SELL" else "⚠️")
    ticker = alert_data.get("ticker", "XAUUSD")
    price = alert_data.get("price", 0.0)
    sl = alert_data.get("sl", 0.0)
    tp1 = alert_data.get("tp1", 0.0)
    tp2 = alert_data.get("tp2", 0.0)
    tp3 = alert_data.get("tp3", 0.0)

    lines = [
        f"{icon} *TradePros SMC Signal Alert*",
        f"━━━━━━━━━━━━━━━━━━━",
        f"📊 *Asset:* `{ticker}`",
        f"🎯 *Action:* *{sig}*",
        f"💰 *Entry:* `{price:.2f}`",
        f"🛑 *Stop Loss:* `{sl:.2f}`"
    ]

    if tp1 > 0:
        lines.append(f"🎯 *TP1:* `{tp1:.2f}`")
    if tp2 > 0:
        lines.append(f"🎯 *TP2:* `{tp2:.2f}`")
    if tp3 > 0:
        lines.append(f"🚀 *TP3:* `{tp3:.2f}`")

    lines.append(f"━━━━━━━━━━━━━━━━━━━")
    lines.append(f"_Trade with proper risk management!_")
    return "\n".join(lines)


def format_discord_webhook(alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format alert as a Discord embed object."""
    sig = alert_data.get("signal", "ALERT").upper()
    color = 0x00FF00 if sig == "BUY" else (0xFF0000 if sig == "SELL" else 0xFFFF00)

    fields = [
        {"name": "Asset", "value": str(alert_data.get("ticker", "XAUUSD")), "inline": True},
        {"name": "Signal", "value": sig, "inline": True},
        {"name": "Entry Price", "value": f"{alert_data.get('price', 0.0):.2f}", "inline": True},
        {"name": "Stop Loss", "value": f"{alert_data.get('sl', 0.0):.2f}", "inline": True}
    ]

    if alert_data.get("tp1", 0.0) > 0:
        fields.append({"name": "TP1", "value": f"{alert_data['tp1']:.2f}", "inline": True})
    if alert_data.get("tp2", 0.0) > 0:
        fields.append({"name": "TP2", "value": f"{alert_data['tp2']:.2f}", "inline": True})

    return {
        "embeds": [
            {
                "title": f"TradePros Alert: {sig} {alert_data.get('ticker', 'XAUUSD')}",
                "color": color,
                "fields": fields,
                "footer": {"text": "TradePros SMC Trading System"}
            }
        ]
    }
