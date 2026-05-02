import pandas as pd

def generate_signals(prices):
    signals = pd.DataFrame(index=prices.index)
    signals['price'] = prices
    
    # 50-day and 200-day moving averages
    signals['ma50'] = prices.rolling(window=50).mean()
    signals['ma200'] = prices.rolling(window=200).mean()
    
    # Buy when 50MA crosses above 200MA, sell when it crosses below
    signals['signal'] = 0
    signals.loc[signals['ma50'] > signals['ma200'], 'signal'] = 1
    signals.loc[signals['ma50'] < signals['ma200'], 'signal'] = -1
    
    return signals

if __name__ == "__main__":
    from data import get_prices
    prices = get_prices("AAPL", "2020-01-01", "2025-01-01")
    signals = generate_signals(prices)
    print(signals.tail(10))