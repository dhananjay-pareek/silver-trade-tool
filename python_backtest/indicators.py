"""
Indicators Module
Technical indicators using pure pandas/numpy (no pandas_ta for Python 3.14 compatibility)
"""

import pandas as pd
import numpy as np


def ema(series: pd.Series, length: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=length, adjust=False).mean()


def sma(series: pd.Series, length: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=length).mean()


def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    """Average True Range."""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=length).mean()


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """MACD - Moving Average Convergence Divergence."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def supertrend(high: pd.Series, low: pd.Series, close: pd.Series, 
               length: int = 10, multiplier: float = 3.0) -> tuple:
    """SuperTrend indicator."""
    atr_val = atr(high, low, close, length)
    hl2 = (high + low) / 2
    
    upper_band = hl2 + (multiplier * atr_val)
    lower_band = hl2 - (multiplier * atr_val)
    
    supertrend = pd.Series(index=close.index, dtype=float)
    direction = pd.Series(index=close.index, dtype=int)
    
    supertrend.iloc[0] = upper_band.iloc[0]
    direction.iloc[0] = 1
    
    for i in range(1, len(close)):
        if close.iloc[i-1] <= supertrend.iloc[i-1]:
            # In downtrend
            supertrend.iloc[i] = upper_band.iloc[i]
            if close.iloc[i] > supertrend.iloc[i]:
                direction.iloc[i] = 1  # Switch to uptrend
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                direction.iloc[i] = -1
                supertrend.iloc[i] = min(supertrend.iloc[i], supertrend.iloc[i-1])
        else:
            # In uptrend
            supertrend.iloc[i] = lower_band.iloc[i]
            if close.iloc[i] < supertrend.iloc[i]:
                direction.iloc[i] = -1  # Switch to downtrend
                supertrend.iloc[i] = upper_band.iloc[i]
            else:
                direction.iloc[i] = 1
                supertrend.iloc[i] = max(supertrend.iloc[i], supertrend.iloc[i-1])
    
    return supertrend, direction


def adx(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> tuple:
    """ADX - Average Directional Index."""
    plus_dm = high.diff()
    minus_dm = -low.diff()
    
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    
    # When +DM > -DM, -DM = 0 and vice versa
    mask = plus_dm > minus_dm
    minus_dm[mask] = 0
    plus_dm[~mask] = 0
    
    atr_val = atr(high, low, close, length)
    
    plus_di = 100 * (plus_dm.rolling(window=length).mean() / atr_val)
    minus_di = 100 * (minus_dm.rolling(window=length).mean() / atr_val)
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    adx_val = dx.rolling(window=length).mean()
    
    return plus_di, minus_di, adx_val


def vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    """Volume Weighted Average Price."""
    typical_price = (high + low + close) / 3
    cumulative_tp_vol = (typical_price * volume).cumsum()
    cumulative_vol = volume.cumsum()
    return cumulative_tp_vol / cumulative_vol


def add_all_indicators(df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
    """
    Add all Trade Expert Pro indicators to the DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
        config: Optional configuration dict for indicator parameters
    
    Returns:
        DataFrame with all indicators added
    """
    if config is None:
        config = get_default_config()
    
    df = df.copy()
    
    # EMAs
    df['EMA9'] = ema(df['Close'], config['ema9'])
    df['EMA21'] = ema(df['Close'], config['ema21'])
    df['EMA50'] = ema(df['Close'], config['ema50'])
    df['EMA200'] = ema(df['Close'], config['ema200'])
    
    # EMA Stack Analysis
    df['BullishStack'] = (df['EMA9'] > df['EMA21']) & (df['EMA21'] > df['EMA50']) & (df['Close'] > df['EMA200'])
    df['BearishStack'] = (df['EMA9'] < df['EMA21']) & (df['EMA21'] < df['EMA50']) & (df['Close'] < df['EMA200'])
    
    # SuperTrend
    st, st_dir = supertrend(df['High'], df['Low'], df['Close'], 
                            config['st_length'], config['st_mult'])
    df['SuperTrend'] = st
    df['ST_Direction'] = st_dir
    df['ST_Bullish'] = st_dir == 1
    df['ST_Bearish'] = st_dir == -1
    
    # ATR
    df['ATR'] = atr(df['High'], df['Low'], df['Close'], config['atr_period'])
    df['ATR_SMA'] = sma(df['ATR'], 50)
    
    # Volatility State
    df['VolRatio'] = df['ATR'] / df['ATR_SMA']
    df['VolState'] = 'NORMAL'
    df.loc[df['VolRatio'] < 0.4, 'VolState'] = 'ULTRA_LOW'
    df.loc[(df['VolRatio'] >= 0.4) & (df['VolRatio'] < 0.7), 'VolState'] = 'LOW'
    df.loc[df['VolRatio'] > 1.5, 'VolState'] = 'HIGH'
    df.loc[df['VolRatio'] > 2.5, 'VolState'] = 'EXTREME'
    
    # RSI
    df['RSI'] = rsi(df['Close'], config['rsi_period'])
    
    # MACD
    macd_line, signal_line, hist = macd(df['Close'], 
                                        config['macd_fast'], 
                                        config['macd_slow'], 
                                        config['macd_signal'])
    df['MACD'] = macd_line
    df['MACD_Signal'] = signal_line
    df['MACD_Hist'] = hist
    
    # ADX & DMI
    plus_di, minus_di, adx_val = adx(df['High'], df['Low'], df['Close'], 14)
    df['ADX'] = adx_val
    df['DI_Plus'] = plus_di
    df['DI_Minus'] = minus_di
    
    # Volume Analysis
    df['VolumeSMA'] = sma(df['Volume'], config['vol_sma'])
    df['VolumeSpike'] = df['Volume'] > df['VolumeSMA'] * config['vol_mult']
    df['RelativeVolume'] = df['Volume'] / df['VolumeSMA']
    
    # VWAP
    df['VWAP'] = vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    
    # Previous Day High/Low
    df['PDH'] = df['High'].shift(1)
    df['PDL'] = df['Low'].shift(1)
    df['PDC'] = df['Close'].shift(1)
    
    # Pivot Points
    df['Pivot'] = (df['PDH'] + df['PDL'] + df['PDC']) / 3
    df['R1'] = 2 * df['Pivot'] - df['PDL']
    df['R2'] = df['Pivot'] + (df['PDH'] - df['PDL'])
    df['S1'] = 2 * df['Pivot'] - df['PDH']
    df['S2'] = df['Pivot'] - (df['PDH'] - df['PDL'])
    
    # Candlestick Analysis
    df['BodySize'] = abs(df['Close'] - df['Open'])
    df['TotalRange'] = df['High'] - df['Low']
    df['UpperWick'] = df['High'] - df[['Open', 'Close']].max(axis=1)
    df['LowerWick'] = df[['Open', 'Close']].min(axis=1) - df['Low']
    df['BullishCandle'] = df['Close'] > df['Open']
    df['BearishCandle'] = df['Close'] < df['Open']
    
    # Engulfing Patterns
    df['BullishEngulfing'] = (df['BullishCandle']) & (df['BearishCandle'].shift(1)) & \
                             (df['Close'] > df['Open'].shift(1)) & (df['Open'] < df['Close'].shift(1))
    df['BearishEngulfing'] = (df['BearishCandle']) & (df['BullishCandle'].shift(1)) & \
                             (df['Close'] < df['Open'].shift(1)) & (df['Open'] > df['Close'].shift(1))
    
    # Hammer & Shooting Star
    df['Hammer'] = (df['LowerWick'] > df['BodySize'] * 2) & (df['UpperWick'] < df['BodySize'] * 0.5)
    df['ShootingStar'] = (df['UpperWick'] > df['BodySize'] * 2) & (df['LowerWick'] < df['BodySize'] * 0.5)
    
    # Structure Breaks
    df['BreakAbove'] = df['Close'] > df['High'].rolling(5).max().shift(1)
    df['BreakBelow'] = df['Close'] < df['Low'].rolling(5).min().shift(1)
    
    # MTF Bias Score
    df['MTFScore'] = 0
    df.loc[df['BullishStack'], 'MTFScore'] += 25
    df.loc[df['BearishStack'], 'MTFScore'] -= 25
    df.loc[df['ST_Bullish'], 'MTFScore'] += 15
    df.loc[df['ST_Bearish'], 'MTFScore'] -= 15
    
    # Bias
    df['Bias'] = 'NEUTRAL'
    df.loc[df['MTFScore'] >= 30, 'Bias'] = 'BULLISH'
    df.loc[df['MTFScore'] <= -30, 'Bias'] = 'BEARISH'
    
    return df


def get_default_config() -> dict:
    """Get default indicator configuration."""
    return {
        'ema9': 9,
        'ema21': 21,
        'ema50': 50,
        'ema200': 200,
        'st_length': 10,
        'st_mult': 3.0,
        'atr_period': 14,
        'rsi_period': 14,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'vol_sma': 20,
        'vol_mult': 1.3,
    }


if __name__ == "__main__":
    # Test indicators
    from data_fetcher import fetch_data, SYMBOLS
    
    print("Fetching data...")
    df = fetch_data(SYMBOLS['NIFTY50'], period='1y', interval='1d')
    
    print("Adding indicators...")
    df = add_all_indicators(df)
    
    print(f"\nIndicators added: {len(df.columns)} columns")
    print(df[['Close', 'EMA9', 'EMA21', 'RSI', 'MACD', 'Bias']].tail(10))
