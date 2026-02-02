"""
Data Fetcher Module
Downloads OHLCV data using yfinance for backtesting
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_data(symbol: str, start_date: str = None, end_date: str = None, 
               interval: str = "1d", period: str = None) -> pd.DataFrame:
    """
    Fetch OHLCV data from Yahoo Finance.
    
    Args:
        symbol: Ticker symbol (e.g., "^NSEI" for Nifty 50, "^NSEBANK" for Bank Nifty)
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        interval: Data interval ('1m', '5m', '15m', '1h', '1d', '1wk')
        period: Alternative to start/end dates ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
    
    Returns:
        DataFrame with OHLCV data
    """
    ticker = yf.Ticker(symbol)
    
    if period:
        df = ticker.history(period=period, interval=interval)
    else:
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        df = ticker.history(start=start_date, end=end_date, interval=interval)
    
    # Clean up column names for backtesting.py compatibility
    df = df.rename(columns={
        'Open': 'Open',
        'High': 'High',
        'Low': 'Low',
        'Close': 'Close',
        'Volume': 'Volume'
    })
    
    # Remove timezone info if present
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    
    # Drop unnecessary columns
    columns_to_keep = ['Open', 'High', 'Low', 'Close', 'Volume']
    df = df[[col for col in columns_to_keep if col in df.columns]]
    
    return df


# Common Indian Market Symbols
SYMBOLS = {
    'NIFTY50': '^NSEI',
    'BANKNIFTY': '^NSEBANK',
    'NIFTYIT': '^CNXIT',
    'SENSEX': '^BSESN',
    # Commodities
    'GOLD': 'GC=F',
    'SILVER': 'SI=F',
    'XAGUSD': 'XAGUSD=X',
    'XAUUSD': 'XAUUSD=X',
    # Forex
    'USDINR': 'INR=X',
    'EURUSD': 'EURUSD=X',
    'GBPUSD': 'GBPUSD=X',
    # Crypto
    'BTCUSD': 'BTC-USD',
    'ETHUSD': 'ETH-USD',
}


def get_symbol(name: str) -> str:
    """Get Yahoo Finance symbol from common name."""
    return SYMBOLS.get(name.upper(), name)


if __name__ == "__main__":
    # Test data fetch
    print("Fetching Nifty 50 data...")
    df = fetch_data(SYMBOLS['NIFTY50'], period='1y', interval='1d')
    print(f"Downloaded {len(df)} candles")
    print(df.tail())
