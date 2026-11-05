# TradePros SMC & Trend Trading System (Gold / XAUUSD)

A complete algorithmic trading framework and TradingView Pine Script v5 system modeled after the live stream strategies featured on **TradeProsTV** / **@sk_analysis** (`https://www.youtube.com/live/KYFMIo1Jb4M`).

---

## 1. System Overview & Core Methodology

The strategy is optimized for high-volatility assets—specifically **Gold (XAUUSD / GC=F)** on intraday timeframes (1-minute, 5-minute, and 15-minute)—integrating Smart Money Concepts (SMC) with dynamic trend-following:

1. **Dynamic Trend Cloud Ribbon (EMA 10 & EMA 30):**
   - Fast EMA (10) and Slow EMA (30) define short-to-medium-term momentum.
   - Dynamic Ribbon Cloud fills the area between the EMAs (green for bullish expansion, red for bearish contraction).
   - **200 EMA Baseline Filter:** Optional long-term baseline ensuring longs are taken only above 200 EMA and shorts only below 200 EMA.

2. **Fair Value Gaps (FVG) / Imbalances:**
   - Detects 3-bar institutional imbalances:
     - **Bullish FVG:** Low of Bar 0 > High of Bar 2.
     - **Bearish FVG:** High of Bar 0 < Low of Bar 2.
   - Automatically projects semi-transparent zone boxes across future candles to identify mitigation and retest opportunities.

3. **Market Structure Breaks (BOS / CHOCH):**
   - Computes swing highs and lows dynamically using pivot lookbacks.
   - **BOS (Break of Structure):** Trend continuation breakout in the direction of the dominant market structure.
   - **CHOCH (Change of Character):** Early reversal signal breaking swing points counter to the dominant trend.

4. **Multi-Target Risk-Reward Projections (SL, TP1, TP2, TP3):**
   - **Stop Loss (SL):** Positioned using ATR-based buffer beyond entry price.
   - **Take Profit Targets:**
     - **TP1 (1:1.5 RR):** Scalp target / partial exit (50% position reduction).
     - **TP2 (1:3.0 RR):** Swing target / core runner.
     - **TP3 (1:4.5 RR):** Extended trend runner.
   - Generates shaded visual projection boxes on the chart upon signal entry.

---

## 2. TradingView Setup Guide

### 2.1 Adding the Indicator (`TradePros_SMC_Indicator.pine`)
1. Open [TradingView](https://www.tradingview.com) and select the **XAUUSD** or **GOLD** chart.
2. Set your timeframe (recommended: **5m** or **1m**).
3. Click on the **Pine Editor** tab at the bottom of the screen.
4. Copy the entire contents of `TradePros_SMC_Indicator.pine` and paste into the editor.
5. Click **Save** and **Add to chart**.

### 2.2 Adding the Strategy (`TradePros_SMC_Strategy.pine`)
1. Open the Pine Editor tab in TradingView.
2. Paste the contents of `TradePros_SMC_Strategy.pine`.
3. Click **Add to chart** to view backtest results, equity curve, profit factor, win rate, and trade list inside the **Strategy Tester** tab.

### 2.3 Configuring TradingView Alert Webhooks
To pipe signals to automated trading bots, Telegram, or Discord:
1. Click the **Alert** button on TradingView.
2. In the **Condition** dropdown, select `TradePros SMC Trend System`.
3. Select either:
   - `TradePros Buy Signal`
   - `TradePros Sell Signal`
4. Set **Trigger** to *Once Per Bar Close*.
5. In the **Webhook URL** field, enter your server endpoint (e.g. `http://your-server-ip:5000/webhook/tradingview`).
6. The alert message uses the default JSON payload configured in the script:
```json
{
  "action": "{{strategy.order.action}}",
  "symbol": "{{ticker}}",
  "price": {{close}},
  "time": "{{time}}",
  "sl": {{plot("SL Level")}},
  "tp1": {{plot("TP1 Level")}},
  "tp2": {{plot("TP2 Level")}}
}
```

---

## 3. Python Algorithmic Engine & Backtesting

This repository includes a production-grade Python library mirroring the Pine Script logic for local simulation, backtesting, and automated webhook handling:

### Directory Structure
```
engine/
├── __init__.py
├── indicators.py      # EMA, ATR, Fair Value Gaps (FVG), Market Structure (BOS/CHOCH)
├── strategy.py        # Confluence signal generator & multi-target calculation
├── backtester.py      # Bar-by-bar backtest simulation & performance metrics
└── alerts.py          # TradingView webhook parser with Discord & Telegram formatters
tests/
└── test_strategy.py   # Complete test suite
```

### Running Tests
Execute the test suite using `pytest`:
```bash
PYTHONPATH=. pytest -v
```

### Running a Backtest in Python
```python
import pandas as pd
from engine.backtester import Backtester

df = pd.read_csv("gold_5m.csv")
bt = Backtester(df, initial_balance=10000.0, risk_per_trade=0.01)
results = bt.run()
bt.print_summary()
```

---

## 4. Recommended Gold (XAUUSD) Settings

| Parameter | Recommended Value | Notes |
|---|---|---|
| Timeframe | 5m / 1m | Optimal balance of FVG formation and trend clarity |
| Fast Ribbon EMA | 10 | Captures quick momentum changes |
| Slow Ribbon EMA | 30 | Smooth baseline support/resistance |
| 200 EMA Filter | Enabled | Filters counter-trend chop |
| ATR Period | 14 | Gold volatility measurement |
| SL ATR Multiple | 1.5 | Sufficient room for Gold intraday wicks |
| TP1 Multiple | 1.5 R:R | Take 50% profit and move SL to breakeven |
| TP2 Multiple | 3.0 R:R | Secondary institutional liquidity target |
| TP3 Multiple | 4.5 R:R | Runner target |
