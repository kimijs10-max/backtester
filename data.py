import yfinance as yf

def get_prices(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    return df['Close'].squeeze()

if __name__ == "__main__":
    prices = get_prices('AAPL', '2020-01-01', '2020-12-31')
    print(prices.head())