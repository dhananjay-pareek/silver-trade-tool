# Silver Expert Core v1.0

A modular, rule-based trading workflow for **Silver (XAGUSD / MCX Silver)** built in TradingView Pine Script v5.

## Features

- ✅ **Non-repainting** - All signals are calculated without lookahead bias
- ✅ **11 Modular Blocks** - Clear pipeline with IF/ELSE gates
- ✅ **Trend & Range Modes** - Automatic regime detection and routing
- ✅ **Multi-Timeframe** - HTF bias analysis with LTF execution
- ✅ **Trade Quality Scoring** - 0-100 score for signal confidence
- ✅ **Risk Management** - Auto SL/TP with RR validation

## Quick Start

1. Open TradingView
2. Go to **Pine Editor**
3. Copy the contents of `SilverExpertCore.pine`
4. Click **Add to Chart**
5. Apply to **XAGUSD** or Silver chart

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| Higher Timeframe | Daily | HTF for trend bias |
| Max Spread | 0.05 | Block trades if spread exceeds |
| ADX Trend Threshold | 22 | ADX above = trend mode |
| ADX Range Threshold | 18 | ADX below = range mode |
| Min Trade Quality | 60 | Required score for signals |
| Min Risk:Reward | 2.0 | Minimum RR to allow trade |

## Workflow Blocks

```
┌─────────────────────────────────────────────────────────────────┐
│                    MARKET VALIDATION                             │
│  Symbol Check → Spread Check → Volatility Check                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ VALID
┌────────────────────────▼────────────────────────────────────────┐
│                VOLATILITY & SESSION                              │
│  ATR(14) → Vol State → Session Detection                         │
└────────────────────────┬────────────────────────────────────────┘
                         │ ALLOWED
┌────────────────────────▼────────────────────────────────────────┐
│                   HTF BIAS BLOCK                                 │
│  EMA 50/200 → Market Structure → ADX Validation → BIAS           │
└────────────────────────┬────────────────────────────────────────┘
                         │ NOT NEUTRAL
┌────────────────────────▼────────────────────────────────────────┐
│              MARKET REGIME DETECTION                             │
│         ADX < 18: RANGE | ADX > 22: TREND                        │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
      ┌──────▼──────┐                 ┌──────▼──────┐
      │ TREND MODE  │                 │ RANGE MODE  │
      │             │                 │             │
      │ Key Levels  │                 │ Range H/L   │
      │ Setup Filter│                 │ Extremes    │
      │ Confirmation│                 │ Rejection   │
      │ Trap Filter │                 │             │
      └──────┬──────┘                 └──────┬──────┘
             │                               │
             └───────────────┬───────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  RISK MANAGEMENT                                 │
│  Stop Loss → Take Profits → RR Validation                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                TRADE QUALITY SCORING                             │
│  HTF Strength + Level Quality + Confirmations + Session          │
└────────────────────────────┬────────────────────────────────────┘
                             │ SCORE >= 60
┌────────────────────────────▼────────────────────────────────────┐
│                  SIGNAL OUTPUT                                   │
│  BUY/SELL + SL + TP1 + TP2 + RR + Quality%                       │
└─────────────────────────────────────────────────────────────────┘
```

## Visual Elements

- **Status Table** - Real-time workflow status (top-right)
- **Key Levels** - PDH/PDL, PWH/PWL, Session Open, Psychological levels
- **Signal Labels** - Entry details with SL, TP, RR, Quality
- **Background** - Subtle color based on HTF bias
- **Bar Colors** - Green for BUY, Red for SELL signals

## Alerts

- **Silver Expert Core - BUY** - Buy signal with details
- **Silver Expert Core - SELL** - Sell signal with details
- **Silver Expert Core - Any Signal** - Either BUY or SELL

## Trade Quality Scoring

| Factor | Max Points |
|--------|------------|
| HTF Trend Strength | 25 |
| Key Level Quality | 25 |
| Confirmation Count | 20 |
| Volatility State | 15 |
| Session Alignment | 15 |
| **Total** | **100** |

## Global No-Trade Conditions

- Major HTF level between entry and target
- Extreme volatility (>2x average ATR)
- Ultra-low volume (<50% average)

## License

Mozilla Public License 2.0
