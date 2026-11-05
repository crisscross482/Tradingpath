# TradePros SMC & Trend Trading System (Gold / XAUUSD)

Complete implementation of the **TradeProsTV** / **@sk_analysis** live stream Gold (XAU/USD) trading indicator and strategy, engineered for **TradingView (Pine Script v5)** and local **Python backtesting/signal execution**.

---

## 📈 System Architecture & Visual Components

The system replicates the exact visual chart indicators and execution framework seen on the live stream:

1. **Dynamic Trend Ribbon / Baseline Cloud**
   - Fast Moving Average (`EMA 10`) & Slow Moving Average (`EMA 30`) forming a dynamic trend cloud.
   - 200 EMA Major Trend Baseline filter to confirm higher timeframe order flow.
2. **Smart Money Concepts (SMC) & ICT Market Structure**
   - **Fair Value Gaps (FVG)**: Identifies 3-candle imbalance zones (Bullish & Bearish) and projects dynamic support/resistance boxes.
   - **Market Structure**: Automatic detection of **Break of Structure (BOS)** and **Change of Character (CHOCH)** based on swing pivots.
3. **Execution Markers & Multi-Target Risk Management**
   - Clear green **BUY** and red **SELL** signal tags plotted directly on price candles.
   - Dynamic ATR-based Stop Loss (`SL`) calculated per setup.
   - Tiered Take Profit target levels:
     - **TP1**: 1:1 Risk-to-Reward (partial scaling)
     - **TP2**: 1:2 Risk-to-Reward (main target)
     - **TP3**: 1:3+ Risk-to-Reward (runner target)
   - Shaded visual Risk/Reward boxes matching TradingView Long/Short position drawing tools.
4. **TradingView Alerts & Webhooks**
   - Pre-configured alert triggers for automatic webhook integration with Telegram, Discord, or automated execution bots.

---

## 📁 Repository Structure

```
├── TradePros_SMC_Indicator.pine  # TradingView Pine Script v5 chart indicator
├── TradePros_SMC_Strategy.pine   # TradingView Pine Script v5 backtesting strategy
├── engine/
│   ├── __init__.py
│   ├── indicators.py             # SMC indicators: EMA, ATR, FVG, BOS, CHOCH
│   ├── strategy.py               # Signal generator and TP/SL confluence engine
│   ├── backtester.py             # Bar-by-bar backtest simulation & metrics
│   └── alerts.py                 # TradingView webhook parser & dispatcher
├── tests/
│   └── test_strategy.py          # Comprehensive unit & integration tests
└── README.md
```

---

## 🚀 TradingView Quickstart Guide

### 1. Adding the Indicator to TradingView
1. Open [TradingView](https://www.tradingview.com) and load the **XAUUSD** (Gold) chart (optimal on 1m, 3m, 5m, or 15m timeframes).
2. Open the **Pine Editor** tab at the bottom of the chart.
3. Copy and paste the contents of `TradePros_SMC_Indicator.pine`.
4. Click **Save** and **Add to chart**.

### 2. Backtesting the Strategy on TradingView
1. In Pine Editor, open a new script and paste the contents of `TradePros_SMC_Strategy.pine`.
2. Click **Add to chart**.
3. View performance metrics (Net Profit, Win Rate, Max Drawdown, Profit Factor) in the **Strategy Tester** tab.

### 3. Setting Up Webhook Alerts
1. In TradingView, click the **Alerts** (Clock) icon on the right panel.
2. Select `TradePros SMC & Trend Trading System` as the condition.
3. In the alert message, use the pre-built template or provide JSON:
```json
{
  "ticker": "{{ticker}}",
  "signal": "{{strategy.order.action}}",
  "price": "{{close}}",
  "sl": "{{plot(\"SL Level\")}}"
}
```

---

## 🐍 Python Engine & Local Testing

### Running Tests
To verify all calculations and simulations locally:
```bash
PYTHONPATH=. pytest -v
```

### Running a Backtest in Python
```python
from engine.backtester import run_backtest

# Provide OHLC price lists (e.g. from MetaTrader 5 or your broker API)
opens = [...]
highs = [...]
lows = [...]
closes = [...]

results = run_backtest(
    opens=opens,
    highs=highs,
    lows=lows,
    closes=closes,
    fast_len=10,
    slow_len=30,
    trend_len=200,
    sl_atr_mult=1.5
)

print(f"Total Trades: {results['total_trades']}")
print(f"Win Rate: {results['win_rate_percent']}%")
print(f"Profit Factor: {results['profit_factor']}")
print(f"Net PnL (Points): {results['net_pnl_points']}")
```

---

## ⚙️ Recommended Settings for Gold (XAUUSD)

| Parameter | Recommended Value | Description |
|---|---|---|
| **Timeframe** | 5m (Intraday) / 1m (Scalping) | Recommended intraday gold session intervals |
| **Fast Ribbon** | 10 EMA | Rapid reaction to pullbacks |
| **Slow Ribbon** | 30 EMA | Trend momentum baseline |
| **Trend Filter** | 200 EMA | Higher-order structural directional bias |
| **ATR Length** | 14 | Volatility measurement |
| **SL Multiplier**| 1.5x ATR | Dynamic buffer below swing / liquidity sweep |
| **TP Targets** | 1.0R / 2.0R / 3.0R | Scaled exit approach for high risk-reward |

---

## ⚖️ Disclaimer
*This repository and indicator system are for educational and research purposes only. Trading financial markets, especially commodities like Gold (XAUUSD), carries substantial risk of loss. Always practice strict risk management.*
