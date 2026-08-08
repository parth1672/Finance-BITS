import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from config import CHARTS_DIR

def setup_charts_dir():
    if not os.path.exists(CHARTS_DIR):
        os.makedirs(CHARTS_DIR)

def plot_price_volume(all_data):
    """
    Generate Price Chart and Volume Chart for every stock.
    all_data is a dict mapping stock_name to its DataFrame.
    """
    setup_charts_dir()
    chart_paths = {}
    
    for stock, df in all_data.items():
        # Price Chart
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df['close'], label='Close Price', color='blue')
        plt.title(f"{stock} - Price vs Date")
        plt.xlabel("Date")
        plt.ylabel("Price (INR)")
        plt.legend()
        plt.grid(True)
        price_path = os.path.join(CHARTS_DIR, f"{stock}_price.png")
        plt.savefig(price_path, bbox_inches='tight')
        plt.close()
        
        # Volume Chart
        plt.figure(figsize=(10, 5))
        plt.bar(df.index, df['volume'], label='Volume', color='orange')
        plt.title(f"{stock} - Volume vs Date")
        plt.xlabel("Date")
        plt.ylabel("Volume")
        plt.legend()
        plt.grid(True)
        volume_path = os.path.join(CHARTS_DIR, f"{stock}_volume.png")
        plt.savefig(volume_path, bbox_inches='tight')
        plt.close()
        
        chart_paths[stock] = {'price': price_path, 'volume': volume_path}
        
    return chart_paths

def plot_portfolio_comparison(perf_df):
    """
    Plot Portfolio Comparison (Bar chart of Return and Std Dev).
    perf_df has index ['Minimum Variance', 'Value Weighted', 'Price Weighted']
    columns ['Return', 'Standard Deviation', 'Sharpe Ratio']
    """
    setup_charts_dir()
    
    x = np.arange(len(perf_df))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar(x - width/2, perf_df['Return'], width, label='Return')
    rects2 = ax.bar(x + width/2, perf_df['Standard Deviation'], width, label='Std Dev')
    
    ax.set_ylabel('Percentage / Value')
    ax.set_title('Portfolio Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(perf_df.index)
    ax.legend()
    
    path = os.path.join(CHARTS_DIR, "portfolio_comparison.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close(fig)
    return path

def plot_risk_return(stats_df):
    """
    Risk Return Scatter Plot of individual stocks.
    """
    setup_charts_dir()
    plt.figure(figsize=(10, 6))
    
    returns = stats_df['Mean Daily Return']
    risks = stats_df['Standard Deviation']
    
    plt.scatter(risks, returns, color='green')
    
    for stock in stats_df.index:
        plt.annotate(stock, (risks[stock], returns[stock]), textcoords="offset points", xytext=(0,10), ha='center')
        
    plt.title("Risk-Return Scatter Plot (Daily)")
    plt.xlabel("Risk (Standard Deviation)")
    plt.ylabel("Expected Return (Mean Daily Return)")
    plt.grid(True)
    
    path = os.path.join(CHARTS_DIR, "risk_return.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    return path

def plot_correlation_heatmap(stock_returns):
    """
    Correlation Heatmap of stock returns.
    """
    setup_charts_dir()
    plt.figure(figsize=(10, 8))
    
    corr = stock_returns.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    
    plt.title("Stock Returns Correlation Heatmap")
    
    path = os.path.join(CHARTS_DIR, "correlation_heatmap.png")
    plt.savefig(path, bbox_inches='tight')
    plt.close()
    return path
