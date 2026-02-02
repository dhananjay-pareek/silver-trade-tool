"""
Trade Expert Pro - Python Backtesting Runner
Main script to run backtests using the Trade Expert Pro strategy
"""

from backtesting import Backtest
import pandas as pd
from datetime import datetime

from data_fetcher import fetch_data, SYMBOLS, get_symbol
from indicators import add_all_indicators, get_default_config
from strategy import TradeExpertPro, TradeExpertProSimple


def run_backtest(symbol: str = '^NSEI', period: str = '2y', interval: str = '1d',
                 initial_cash: float = 1000000, commission: float = 0.001,
                 strategy_class = TradeExpertPro, show_plot: bool = True) -> dict:
    """
    Run a backtest on the given symbol.
    
    Args:
        symbol: Yahoo Finance ticker symbol
        period: Data period ('1y', '2y', '5y', 'max')
        interval: Data interval ('1d', '1h', etc.)
        initial_cash: Starting capital (default: Rs.10,00,000)
        commission: Commission per trade (default: 0.1%)
        strategy_class: Strategy class to use
        show_plot: Whether to show interactive plot
    
    Returns:
        Dictionary with backtest results
    """
    print(f"\n{'='*60}")
    print(f"TRADE EXPERT PRO - PYTHON BACKTEST")
    print(f"{'='*60}")
    print(f"Symbol: {symbol}")
    print(f"Period: {period}")
    print(f"Interval: {interval}")
    print(f"Initial Capital: Rs.{initial_cash:,.0f}")
    print(f"{'='*60}\n")
    
    # Fetch data
    print("[*] Fetching data...")
    df = fetch_data(symbol, period=period, interval=interval)
    print(f"    Downloaded {len(df)} candles from {df.index[0]} to {df.index[-1]}")
    
    # Add indicators
    print("[*] Computing indicators...")
    df = add_all_indicators(df)
    
    # Drop rows with NaN values (from indicator warm-up)
    df = df.dropna()
    print(f"    Ready for backtest: {len(df)} candles with {len(df.columns)} features")
    
    # Run backtest
    print("\n[*] Running backtest...")
    bt = Backtest(
        df,
        strategy_class,
        cash=initial_cash,
        commission=commission,
        exclusive_orders=True,
        trade_on_close=True
    )
    
    results = bt.run()
    
    # Print results
    print(f"\n{'='*60}")
    print("BACKTEST RESULTS")
    print(f"{'='*60}")
    print(f"Total Return:        {results['Return [%]']:.2f}%")
    print(f"Buy & Hold Return:   {results['Buy & Hold Return [%]']:.2f}%")
    print(f"Max Drawdown:        {results['Max. Drawdown [%]']:.2f}%")
    print(f"Win Rate:            {results['Win Rate [%]']:.2f}%")
    print(f"Total Trades:        {results['# Trades']}")
    print(f"Avg Trade Duration:  {results['Avg. Trade Duration']}")
    print(f"Sharpe Ratio:        {results['Sharpe Ratio']:.2f}")
    print(f"Profit Factor:       {results['Profit Factor']:.2f}" if results['Profit Factor'] else "N/A")
    print(f"Expectancy:          {results['Expectancy [%]']:.2f}%")
    print(f"{'='*60}\n")
    
    # Show plot
    if show_plot:
        print("[*] Opening interactive chart...")
        bt.plot(open_browser=True, filename=f'backtest_{symbol.replace("^", "")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
    
    return {
        'results': results,
        'backtest': bt,
        'data': df
    }


def optimize_strategy(symbol: str = '^NSEI', period: str = '2y'):
    """
    Optimize strategy parameters.
    """
    print("\n[*] Running parameter optimization...")
    
    df = fetch_data(symbol, period=period)
    df = add_all_indicators(df)
    df = df.dropna()
    
    bt = Backtest(
        df,
        TradeExpertPro,
        cash=1000000,
        commission=0.001,
        exclusive_orders=True
    )
    
    # Optimize key parameters
    stats, heatmap = bt.optimize(
        min_quality=[40, 50, 60],
        min_rr=[1.0, 1.5, 2.0],
        tp2_rr=[1.5, 2.0, 2.5, 3.0],
        maximize='Return [%]',
        return_heatmap=True
    )
    
    print("\n[+] Optimal Parameters:")
    print(f"    min_quality: {stats._strategy.min_quality}")
    print(f"    min_rr: {stats._strategy.min_rr}")
    print(f"    tp2_rr: {stats._strategy.tp2_rr}")
    print(f"\n    Best Return: {stats['Return [%]']:.2f}%")
    
    return stats, heatmap


def compare_markets():
    """
    Compare strategy performance across different markets.
    """
    markets = {
        'Nifty 50': '^NSEI',
        'Bank Nifty': '^NSEBANK',
        'Gold': 'GC=F',
        'Silver': 'SI=F',
    }
    
    results = {}
    
    for name, symbol in markets.items():
        try:
            print(f"\n[*] Testing {name}...")
            res = run_backtest(symbol, period='2y', show_plot=False)
            results[name] = {
                'Return': res['results']['Return [%]'],
                'Max DD': res['results']['Max. Drawdown [%]'],
                'Win Rate': res['results']['Win Rate [%]'],
                'Trades': res['results']['# Trades'],
                'Sharpe': res['results']['Sharpe Ratio']
            }
        except Exception as e:
            print(f"    [X] Error: {e}")
    
    # Print comparison
    print(f"\n{'='*80}")
    print("MARKET COMPARISON")
    print(f"{'='*80}")
    print(f"{'Market':<15} {'Return %':>12} {'Max DD %':>12} {'Win Rate %':>12} {'Trades':>10} {'Sharpe':>10}")
    print("-" * 80)
    
    for name, stats in results.items():
        print(f"{name:<15} {stats['Return']:>12.2f} {stats['Max DD']:>12.2f} {stats['Win Rate']:>12.2f} {stats['Trades']:>10} {stats['Sharpe']:>10.2f}")
    
    return results


if __name__ == "__main__":
    # Run backtest on Nifty 50
    result = run_backtest(
        symbol='^NSEI',
        period='2y',
        interval='1d',
        initial_cash=1000000,
        strategy_class=TradeExpertPro,
        show_plot=True
    )
    
    # Uncomment to run optimization
    # optimize_strategy()
    
    # Uncomment to compare markets
    # compare_markets()
