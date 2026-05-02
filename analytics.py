import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze(portfolio, signals):
    from data import get_prices

    # Total return
    total_return = (portfolio['value'].iloc[-1] / portfolio['value'].iloc[0] - 1) * 100

    # Sharpe ratio
    daily_returns = portfolio['value'].pct_change().dropna()
    sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)

    # Max drawdown
    rolling_max = portfolio['value'].cummax()
    drawdown = (portfolio['value'] - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100

    print(f"Total return:  {total_return:.1f}%")
    print(f"Sharpe ratio:  {sharpe:.2f}")
    print(f"Max drawdown:  {max_drawdown:.1f}%")

    # Get S&P 500 data for same period
    start = portfolio.index[0].strftime('%Y-%m-%d')
    end = portfolio.index[-1].strftime('%Y-%m-%d')
    spy_prices = get_prices("SPY", start, end)

    # Normalise both to start at $10,000
    spy_normalised = (spy_prices / spy_prices.iloc[0]) * portfolio['value'].iloc[0]

    # S&P 500 return
    start = portfolio.index[0].strftime('%Y-%m-%d')
    end = portfolio.index[-1].strftime('%Y-%m-%d')
    spy_prices = get_prices("SPY", start, end)
    spy_prices = spy_prices.squeeze()

    # Normalise both to start at $10,000
    spy_start = spy_prices.dropna().iloc[0]
    spy_end = spy_prices.dropna().iloc[-1]
    spy_normalised = (spy_prices / spy_start) * portfolio['value'].iloc[0]

    # S&P 500 return
    spy_return = (spy_end / spy_start - 1) * 100
    print(f"S&P 500 return: {float(spy_return):.1f}%")
    print(f"Outperformance: {float(total_return - spy_return):.1f}%")
    # Plot both
    plt.figure(figsize=(12, 5))
    plt.plot(portfolio.index, portfolio['value'], label='Your strategy', color='blue')
    plt.plot(spy_normalised.index, spy_normalised, label='S&P 500', color='orange', linestyle='--')
    plt.title('Your strategy vs S&P 500')
    plt.xlabel('Date')
    plt.ylabel('Value ($)')
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    from data import get_prices
    from strategy import generate_signals
    from backtest import run_backtest

    prices = get_prices("AAPL", "2020-01-01", "2025-01-01")
    signals = generate_signals(prices)
    portfolio = run_backtest(signals)
    analyze(portfolio, signals)


