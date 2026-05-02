import pandas as pd

def run_backtest(signals, initial_cash=10000):
    cash = initial_cash
    shares = 0
    portfolio = []

    for date, row in signals.iterrows():
        price = row['price']

        # Buy
        if row['signal'] == 1 and cash > 0:
            shares = cash / price
            cash = 0

        # Sell
        elif row['signal'] == -1 and shares > 0:
            cash = shares * price
            shares = 0

        # Track total value each day
        total_value = cash + (shares * price)
        portfolio.append({'date': date, 'value': total_value})

    return pd.DataFrame(portfolio).set_index('date')

if __name__ == "__main__":
    from data import get_prices
    from strategy import generate_signals

    prices = get_prices("AAPL", "2020-01-01", "2025-01-01")
    signals = generate_signals(prices)
    portfolio = run_backtest(signals)
    print(portfolio.tail(10))