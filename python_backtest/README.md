# Trade Expert Pro - Python Backtesting Framework

A Python implementation of the Trade Expert Pro trading strategy, converted from Pine Script for unlimited backtesting capabilities.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd python_backtest
pip install -r requirements.txt
```

### 2. Run Backtest
```bash
python run_backtest.py
```

## 📁 Project Structure

```
python_backtest/
├── requirements.txt    # Python dependencies
├── data_fetcher.py     # Download data via yfinance
├── indicators.py       # Technical indicators (pandas_ta)
├── strategy.py         # Trade Expert Pro strategy class
├── run_backtest.py     # Main runner script
└── README.md           # This file
```

## 📊 Available Symbols

| Market | Symbol |
|--------|--------|
| Nifty 50 | `^NSEI` |
| Bank Nifty | `^NSEBANK` |
| Sensex | `^BSESN` |
| Gold | `GC=F` |
| Silver | `SI=F` |
| BTC/USD | `BTC-USD` |

## 🔧 Usage Examples

### Basic Backtest
```python
from run_backtest import run_backtest

result = run_backtest(
    symbol='^NSEI',      # Nifty 50
    period='2y',         # 2 years of data
    initial_cash=1000000 # ₹10 Lakhs
)
```

### Compare Multiple Markets
```python
from run_backtest import compare_markets
results = compare_markets()
```

### Optimize Parameters
```python
from run_backtest import optimize_strategy
stats, heatmap = optimize_strategy('^NSEI', '2y')
```

## 📈 Strategy Features

- **Multi-Timeframe Analysis**: EMA Stack (9, 21, 50, 200)
- **SuperTrend**: Trend confirmation
- **Volume Analysis**: Spike detection
- **Candlestick Patterns**: Engulfing, Hammer, Shooting Star
- **Risk Management**: ATR-based SL/TP, position sizing
- **Quality Scoring**: 0-100 trade quality assessment

## 📋 Output Metrics

| Metric | Description |
|--------|-------------|
| Return % | Total return |
| Max Drawdown | Worst peak-to-trough decline |
| Win Rate | Percentage of profitable trades |
| Sharpe Ratio | Risk-adjusted return |
| Profit Factor | Gross profit / Gross loss |

## ⚠️ Notes

- Yahoo Finance data may have delays/gaps
- Use `1d` interval for most reliable data
- Intraday data limited to 60 days on free tier
- Results are for educational purposes only
