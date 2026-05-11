import yfinance as yf
import pandas as pd
import numpy as np

TICKERS = [
    # Your actual holdings
    "4180.T", "5105.T", "8306.T", "NVDA", "SHOP",

    # US large cap
    "AAPL", "MSFT", "GOOGL", "JPM", "BAC", "WFC", "XOM", "CVX",
    "JNJ", "PFE", "KO", "PEP", "WMT", "TGT", "F", "GM",
    "BRK-B", "V", "MA", "UNH", "HD", "MCD", "DIS", "NFLX",

    # US value plays
    "C", "GS", "MS", "T", "VZ", "IBM", "INTC", "MO",

    # Japanese large cap
    "7203.T", "6758.T", "9984.T", "7267.T", "6501.T",
    "9432.T", "4063.T", "6861.T", "8058.T", "8031.T",
    "7974.T", "9983.T",
]



def get_fundamentals(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials
        balance_sheet = stock.balance_sheet

        # Detect if this is a financial/bank stock
        sector = info.get('sector', '')
        is_bank = sector in ['Financial Services', 'Banks', 'Diversified Financials']

        # --- Basic value metrics ---
        pe = info.get('trailingPE', None)
        pb = info.get('priceToBook', None)
        roe = info.get('returnOnEquity', None)

        # --- Debt/Equity (skip for banks) ---
        de_ratio = None
        if not is_bank:
            de_ratio = info.get('debtToEquity', None)
            if de_ratio:
                de_ratio = de_ratio / 100

        # --- Liquidity ratios ---
        current_ratio = info.get('currentRatio', None)
        quick_ratio = info.get('quickRatio', None)

        # --- Bank specific metrics ---
        roa = info.get('returnOnAssets', None)

        # --- Earnings momentum ---
        earnings_momentum = None
        if financials is not None and not financials.empty:
            try:
                net_income = financials.loc['Net Income']
                if len(net_income) >= 2:
                    earnings_momentum = (net_income.iloc[0] - net_income.iloc[1]) / abs(net_income.iloc[1])
            except:
                pass

        # --- Piotroski F-Score ---
        f_score = 0
        try:
            if roa and roa > 0: f_score += 1
            if roe and roe > 0: f_score += 1
            if current_ratio and current_ratio > 1: f_score += 1
            if not is_bank:
                if de_ratio is not None and de_ratio < 1: f_score += 1
                if quick_ratio and quick_ratio > 1: f_score += 1
            else:
                # For banks: reward positive ROA and good P/B instead
                if roa and roa > 0.005: f_score += 1  # banks have naturally low ROA
                if pb and pb < 2: f_score += 1         # cheap relative to book value
            gross_margin = info.get('grossMargins', None)
            if gross_margin and gross_margin > 0: f_score += 1
            asset_turnover = info.get('assetTurnover', None)
            if asset_turnover and asset_turnover > 0: f_score += 1
            if earnings_momentum and earnings_momentum > 0: f_score += 1
            op_margin = info.get('operatingMargins', None)
            if op_margin and op_margin > 0: f_score += 1
        except:
            pass

        return {
            'ticker': ticker,
            'pe_ratio': pe,
            'pb_ratio': pb,
            'roe': roe,
            'de_ratio': de_ratio,
            'current_ratio': current_ratio,
            'quick_ratio': quick_ratio,
            'earnings_momentum': earnings_momentum,
            'f_score': f_score,
            'is_bank': is_bank,
            'roa': roa,
        }

    except Exception as e:
        print(f"  Error fetching {ticker}: {e}")
        return None

def score_stocks(df):
    scores = pd.DataFrame(index=df.index)

    scores['pe_rank']  = df['pe_ratio'].rank(ascending=True)
    scores['pb_rank']  = df['pb_ratio'].rank(ascending=True)
    scores['roe_rank'] = df['roe'].rank(ascending=False)
    scores['em_rank']  = df['earnings_momentum'].rank(ascending=False)
    scores['fs_rank']  = df['f_score'].rank(ascending=False)

    # Only rank D/E and liquidity for non-banks
    non_bank_mask = df['is_bank'] == False
    scores['de_rank'] = 0.0
    scores['cr_rank'] = 0.0
    scores['qr_rank'] = 0.0

    if non_bank_mask.any():
        scores.loc[non_bank_mask, 'de_rank'] = df.loc[non_bank_mask, 'de_ratio'].rank(ascending=True)
        scores.loc[non_bank_mask, 'cr_rank'] = df.loc[non_bank_mask, 'current_ratio'].rank(ascending=False)
        scores.loc[non_bank_mask, 'qr_rank'] = df.loc[non_bank_mask, 'quick_ratio'].rank(ascending=False)

    # For banks: use ROA rank instead
    bank_mask = df['is_bank'] == True
    scores['roa_rank'] = 0.0
    if bank_mask.any():
        scores.loc[bank_mask, 'roa_rank'] = df.loc[bank_mask, 'roa'].rank(ascending=False)

    df['value_score'] = (
        scores['pe_rank']  * 1.0 +
        scores['pb_rank']  * 1.0 +
        scores['roe_rank'] * 1.0 +
        scores['de_rank']  * 1.5 +
        scores['cr_rank']  * 1.5 +
        scores['qr_rank']  * 1.5 +
        scores['em_rank']  * 1.0 +
        scores['fs_rank']  * 2.0 +
        scores['roa_rank'] * 1.5   # bank specific
    )

    return df

def screen_stocks():
    print("Fetching fundamentals for all tickers...\n")
    data = []
    for ticker in TICKERS:
        result = get_fundamentals(ticker)
        if result:
            data.append(result)
        print(f"  {ticker} done")

    # Build dataframe and drop rows with too many missing values
    df = pd.DataFrame(data)
    df = df.dropna(thresh=6)  # keep rows with at least 6 out of 9 factors
    df = df.set_index('ticker')

    # Fill remaining NaN with median so ranking still works
    df = df.fillna(df.median(numeric_only=True))

    # Score and rank
    df = score_stocks(df)
    df = df.sort_values('value_score')

    # Display results
    print("\n" + "="*70)
    print("TOP 10 VALUE STOCKS (9-factor model)")
    print("="*70)
    display_cols = ['pe_ratio', 'pb_ratio', 'roe', 'de_ratio',
                    'current_ratio', 'quick_ratio', 'earnings_momentum',
                    'f_score', 'value_score']
    pd.set_option('display.float_format', '{:.2f}'.format)
    print(df[display_cols].head(10).to_string())

    print("\n" + "="*70)
    print("YOUR HOLDINGS RANKING:")
    print("="*70)
    your_holdings = ['4180.T', '5105.T', '8306.T', 'NVDA', 'SHOP']
    holdings_in_df = [t for t in your_holdings if t in df.index]
    print(df.loc[holdings_in_df, display_cols].to_string())

    return df.head(10).index.tolist()

if __name__ == "__main__":
    top10 = screen_stocks()
    print(f"\nSelected for portfolio: {top10}")