# UT Bot + Structure Fusion Trading System

High-performance trading system combining UT Bot ATR trailing-stop signals with dynamic market structure pivots (BOS / CHoCH), multi-target risk-reward projections, breakeven management, and an on-chart statistics dashboard.

---

## 1. Indicator Overview (`TradePros_SMC_Indicator.pine`)

- **Pine Script Version:** `@version=6`
- **Signal Engine:** Fast UT Bot ATR-based trailing stop (`sensitivity = 2.0`, `utAtrPeriod = 1`).
- **Entry Modes:**
  1. `UT Bot Only`: Direct trailing-stop flips.
  2. `UT Bot + Structure Confluence`: UT Bot signal filtered by structure trend alignment.
  3. `Structure Breakout (CHoCH)`: Directly trades swing structure breakout flips.
- **Stop Loss / Take Profit Modes:**
  - `Structure`: Validated swing levels with ATR floor and fallback multiplier.
  - `ATR-Based`: Dynamic ATR multiples.
  - `Fixed Distance`: Fixed price units or pips.
- **Breakeven Engine:** Automatically steps stop loss to entry price (plus configurable offset) upon reaching TP1, TP2, or TP3.
- **On-Chart Performance Dashboard:** Displays Today, This Week, This Month, and All-Time signals, trades, win rate, net R, and expectancy (Avg R).
- **Webhooks & Alert Conditions:**
  - `Long Entry`
  - `Short Entry`
  - `Breakeven`
  - `Opposite-Signal Exit`

---

## 2. Pine Script Strategy (`TradePros_SMC_Strategy.pine`)

Designed for TradingView Strategy Tester with automated position execution, structure-derived stop loss, and target exits.

---

## 3. Python Algorithmic Engine & Backtesting

The repository includes a modular Python engine under `engine/`:
- `engine/indicators.py`: Calculations for ATR, EMA, Fair Value Gaps, and Market Structure pivots.
- `engine/strategy.py`: Signal generator and confluence evaluator.
- `engine/backtester.py`: Bar-by-bar backtester simulating risk-reward and expectancy.
- `engine/alerts.py`: Webhook receiver parsing TradingView alert payloads and formatting Telegram/Discord notifications.

### Running Python Tests
```bash
PYTHONPATH=. pytest -v
```
