import yfinance as yf

def get_prices(ticker, start_date, end_date):
    df = yf.download(ticker, start = start_date, end = end_date)
    return df['Close']

if __name__ == "__main__":
    prices = get_prices('AAPL', '2020-01-01', '2020-12-31')
    print(prices.head())