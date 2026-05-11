import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from screener import screen_stocks, TICKERS
import pandas as pd

def plot_pe_vs_roe(df):
    fig, ax = plt.subplots(figsize=(14, 8))

    # Colour banks differently
    colors = ['#e74c3c' if is_bank else '#3498db' for is_bank in df['is_bank']]

    # Size bubbles by F-score
    sizes = df['f_score'] * 40

    scatter = ax.scatter(
        df['pe_ratio'],
        df['roe'],
        c=colors,
        s=sizes,
        alpha=0.7,
        edgecolors='white',
        linewidth=0.5
    )

    # Label your actual holdings
    your_holdings = ['4180.T', '5105.T', '8306.T', 'NVDA', 'SHOP']
    for ticker in your_holdings:
        if ticker in df.index:
            ax.annotate(
                ticker,
                (df.loc[ticker, 'pe_ratio'], df.loc[ticker, 'roe']),
                fontsize=9,
                fontweight='bold',
                color='black',
                xytext=(8, 4),
                textcoords='offset points'
            )

    # Label top 10
    top10 = df.nsmallest(10, 'value_score')
    for ticker in top10.index:
        if ticker not in your_holdings:
            ax.annotate(
                ticker,
                (df.loc[ticker, 'pe_ratio'], df.loc[ticker, 'roe']),
                fontsize=7,
                color='gray',
                xytext=(8, 4),
                textcoords='offset points'
            )

    # Reference lines
    ax.axvline(x=df['pe_ratio'].median(), color='gray', linestyle='--', alpha=0.4, label='Median P/E')
    ax.axhline(y=df['roe'].median(), color='gray', linestyle=':', alpha=0.4, label='Median ROE')

    # Labels
    ax.set_xlabel('P/E Ratio (lower = cheaper)', fontsize=12)
    ax.set_ylabel('Return on Equity (higher = better)', fontsize=12)
    ax.set_title('9-Factor Value Screener: P/E vs ROE\nBubble size = F-Score | Red = Banks | Blue = Non-banks', fontsize=13)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498db', markersize=10, label='Non-bank'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#e74c3c', markersize=10, label='Bank'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=6, label='Small bubble = low F-score'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=12, label='Large bubble = high F-score'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

    plt.tight_layout()
    plt.show()

def plot_holdings_radar(df):
    your_holdings = ['4180.T', '5105.T', '8306.T', 'NVDA', 'SHOP']
    holdings = [t for t in your_holdings if t in df.index]

    metrics = ['pe_ratio', 'pb_ratio', 'roe', 'current_ratio', 'f_score']
    labels = ['P/E', 'P/B', 'ROE', 'Current Ratio', 'F-Score']

    # Normalise 0-1 for radar
    df_norm = df[metrics].copy()
    for col in metrics:
        df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    # Invert P/E and P/B so higher = better on radar
    df_norm['pe_ratio'] = 1 - df_norm['pe_ratio']
    df_norm['pb_ratio'] = 1 - df_norm['pb_ratio']

    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

    for i, ticker in enumerate(holdings):
        values = df_norm.loc[ticker, metrics].tolist()
        values += values[:1]
        ax.plot(angles, values, color=colors[i], linewidth=2, label=ticker)
        ax.fill(angles, values, color=colors[i], alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_title('Your Holdings — Factor Comparison\n(higher = better on each axis)', fontsize=13, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Running screener...")
    df = screen_stocks()

    # Convert top10 list back to full df
    import yfinance as yf
    from screener import get_fundamentals, score_stocks
    import pandas as pd

    data = []
    for ticker in TICKERS:
        result = get_fundamentals(ticker)
        if result:
            data.append(result)

    full_df = pd.DataFrame(data).dropna(thresh=6).set_index('ticker')
    full_df = full_df.fillna(full_df.median(numeric_only=True))
    full_df = score_stocks(full_df)

    print("\nGenerating visualisations...")
    plot_pe_vs_roe(full_df)
    plot_holdings_radar(full_df)
    