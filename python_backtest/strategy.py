"""
Trade Expert Pro Strategy
Converted from Pine Script to Python using backtesting.py
"""

from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np


class TradeExpertPro(Strategy):
    """
    Trade Expert Pro v2.0 Strategy
    
    A multi-layer, institutional-grade trading strategy with:
    - Multi-timeframe confluence
    - Smart money detection
    - Trap avoidance
    - Dynamic position sizing
    """
    
    # Strategy Parameters (can be optimized)
    min_quality = 50
    a_grade_min = 65
    a_plus_min = 80
    min_rr = 1.5
    tp1_rr = 1.0
    tp2_rr = 2.0
    tp3_rr = 3.0
    sl_buffer = 0.2
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        """Initialize indicators (already computed in DataFrame)."""
        # Access pre-computed indicators from the data
        self.ema9 = self.I(lambda: self.data.EMA9)
        self.ema21 = self.I(lambda: self.data.EMA21)
        self.ema50 = self.I(lambda: self.data.EMA50)
        self.ema200 = self.I(lambda: self.data.EMA200)
        self.supertrend = self.I(lambda: self.data.SuperTrend)
        self.rsi = self.I(lambda: self.data.RSI)
        self.atr = self.I(lambda: self.data.ATR)
        self.macd = self.I(lambda: self.data.MACD)
        self.macd_signal = self.I(lambda: self.data.MACD_Signal)
        
    def get_quality_score(self) -> int:
        """Calculate trade quality score (0-100)."""
        score = 0
        
        # MTF Score contribution (20%)
        mtf_score = abs(self.data.MTFScore[-1]) if hasattr(self.data, 'MTFScore') else 0
        score += min(20, mtf_score / 100 * 20)
        
        # EMA Stack (15%)
        if self.data.BullishStack[-1] or self.data.BearishStack[-1]:
            score += 15
        
        # SuperTrend alignment (10%)
        bias = self.data.Bias[-1]
        if (bias == 'BULLISH' and self.data.ST_Bullish[-1]) or \
           (bias == 'BEARISH' and self.data.ST_Bearish[-1]):
            score += 10
        
        # RSI confirmation (10%)
        rsi = self.data.RSI[-1]
        if (bias == 'BULLISH' and 30 < rsi < 70) or \
           (bias == 'BEARISH' and 30 < rsi < 70):
            score += 10
        
        # MACD confirmation (10%)
        if (bias == 'BULLISH' and self.data.MACD[-1] > self.data.MACD_Signal[-1]) or \
           (bias == 'BEARISH' and self.data.MACD[-1] < self.data.MACD_Signal[-1]):
            score += 10
        
        # Volume spike (10%)
        if self.data.VolumeSpike[-1]:
            score += 10
        
        # Candlestick pattern (10%)
        if (bias == 'BULLISH' and (self.data.BullishEngulfing[-1] or self.data.Hammer[-1])) or \
           (bias == 'BEARISH' and (self.data.BearishEngulfing[-1] or self.data.ShootingStar[-1])):
            score += 10
        
        # Structure break (10%)
        if (bias == 'BULLISH' and self.data.BreakAbove[-1]) or \
           (bias == 'BEARISH' and self.data.BreakBelow[-1]):
            score += 10
        
        # Normal volatility (5%)
        if self.data.VolState[-1] == 'NORMAL':
            score += 5
        
        return min(100, int(score))
    
    def get_sl_tp(self, is_long: bool) -> tuple:
        """Calculate Stop Loss and Take Profit levels."""
        atr = self.data.ATR[-1]
        close = self.data.Close[-1]
        
        if is_long:
            # Use recent swing low or ATR-based
            recent_low = min(self.data.Low[-5:])
            sl = min(recent_low - atr * self.sl_buffer, close - atr * 1.2)
            risk = close - sl
            tp1 = close + risk * self.tp1_rr
            tp2 = close + risk * self.tp2_rr
            tp3 = close + risk * self.tp3_rr
        else:
            # Short position
            recent_high = max(self.data.High[-5:])
            sl = max(recent_high + atr * self.sl_buffer, close + atr * 1.2)
            risk = sl - close
            tp1 = close - risk * self.tp1_rr
            tp2 = close - risk * self.tp2_rr
            tp3 = close - risk * self.tp3_rr
        
        return sl, tp1, tp2, tp3
    
    def check_veto_conditions(self) -> tuple:
        """Check if any veto conditions are active."""
        # Extreme volatility
        if self.data.VolState[-1] in ['ULTRA_LOW', 'EXTREME']:
            return True, f"Volatility: {self.data.VolState[-1]}"
        
        # No clear bias
        if self.data.Bias[-1] == 'NEUTRAL':
            return True, "No MTF Confluence"
        
        return False, ""
    
    def next(self):
        """Main strategy logic - called on each bar."""
        # Skip if we already have a position
        if self.position:
            return
        
        # Check veto conditions
        vetoed, reason = self.check_veto_conditions()
        if vetoed:
            return
        
        # Get quality score
        quality = self.get_quality_score()
        if quality < self.min_quality:
            return
        
        bias = self.data.Bias[-1]
        
        # BULLISH SIGNAL
        if bias == 'BULLISH':
            # Check confirmations
            confirmations = 0
            if self.data.BullishStack[-1]:
                confirmations += 1
            if self.data.ST_Bullish[-1]:
                confirmations += 1
            if self.data.MACD[-1] > self.data.MACD_Signal[-1]:
                confirmations += 1
            if self.data.RSI[-1] > 40 and self.data.RSI[-1] < 70:
                confirmations += 1
            if self.data.VolumeSpike[-1]:
                confirmations += 1
            
            if confirmations >= 3:
                sl, tp1, tp2, tp3 = self.get_sl_tp(is_long=True)
                rr = (tp2 - self.data.Close[-1]) / (self.data.Close[-1] - sl) if (self.data.Close[-1] - sl) > 0 else 0
                
                if rr >= self.min_rr:
                    # Use fixed 50% position size for simplicity
                    self.buy(size=0.5, sl=sl, tp=tp2)
        
        # BEARISH SIGNAL
        elif bias == 'BEARISH':
            # Check confirmations
            confirmations = 0
            if self.data.BearishStack[-1]:
                confirmations += 1
            if self.data.ST_Bearish[-1]:
                confirmations += 1
            if self.data.MACD[-1] < self.data.MACD_Signal[-1]:
                confirmations += 1
            if self.data.RSI[-1] < 60 and self.data.RSI[-1] > 30:
                confirmations += 1
            if self.data.VolumeSpike[-1]:
                confirmations += 1
            
            if confirmations >= 3:
                sl, tp1, tp2, tp3 = self.get_sl_tp(is_long=False)
                rr = (self.data.Close[-1] - tp2) / (sl - self.data.Close[-1]) if (sl - self.data.Close[-1]) > 0 else 0
                
                if rr >= self.min_rr:
                    # Use fixed 50% position size for simplicity
                    self.sell(size=0.5, sl=sl, tp=tp2)


class TradeExpertProSimple(Strategy):
    """
    Simplified version for quick testing.
    Uses basic EMA crossover with SuperTrend confirmation.
    """
    
    def init(self):
        self.ema9 = self.I(lambda: self.data.EMA9)
        self.ema21 = self.I(lambda: self.data.EMA21)
        
    def next(self):
        if self.position:
            return
        
        # Simple crossover strategy
        if crossover(self.data.EMA9, self.data.EMA21):
            if self.data.ST_Bullish[-1]:
                sl = self.data.Close[-1] - self.data.ATR[-1] * 1.5
                tp = self.data.Close[-1] + self.data.ATR[-1] * 3
                self.buy(sl=sl, tp=tp)
        
        elif crossover(self.data.EMA21, self.data.EMA9):
            if self.data.ST_Bearish[-1]:
                sl = self.data.Close[-1] + self.data.ATR[-1] * 1.5
                tp = self.data.Close[-1] - self.data.ATR[-1] * 3
                self.sell(sl=sl, tp=tp)
