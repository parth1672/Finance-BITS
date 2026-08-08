import os
import pandas as pd
from config import STOCKS_DIR, INDEX_DIR

def get_stock_name(filename):
    """Extract stock ticker from filename (e.g. 'BHARTIARTL-10604.csv' -> 'BHARTIARTL')"""
    return filename.split('-')[0]

def load_and_merge_stocks():
    """
    Reads all stock CSVs from Data/stocks, merges them on Date,
    and returns a DataFrame of closing prices.
    Also returns a dictionary with all original data mapped by stock.
    """
    all_data = {}
    close_prices = pd.DataFrame()
    volume_data = pd.DataFrame()
    
    files = [f for f in os.listdir(STOCKS_DIR) if f.endswith('.csv')]
    for file in files:
        stock_name = get_stock_name(file)
        filepath = os.path.join(STOCKS_DIR, file)
        
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        all_data[stock_name] = df
        
        # Merge closing prices
        if close_prices.empty:
            close_prices = df[['close']].rename(columns={'close': stock_name})
            volume_data = df[['volume']].rename(columns={'volume': stock_name})
        else:
            close_prices = close_prices.join(df[['close']].rename(columns={'close': stock_name}), how='outer')
            volume_data = volume_data.join(df[['volume']].rename(columns={'volume': stock_name}), how='outer')
            
    # Sort by date and remove missing rows as per Task 1
    close_prices.sort_index(inplace=True)
    close_prices.dropna(inplace=True)
    
    volume_data.sort_index(inplace=True)
    volume_data = volume_data.loc[close_prices.index]
    
    return close_prices, volume_data, all_data

def load_index():
    """Reads NIFTY index data from Data/index"""
    files = [f for f in os.listdir(INDEX_DIR) if f.endswith('.csv')]
    if not files:
        raise FileNotFoundError("Index CSV not found in index directory")
        
    filepath = os.path.join(INDEX_DIR, files[0])
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)
    return df

def compute_daily_returns(prices_df):
    """
    Compute Daily Returns
    Formula: (Current Close - Previous Close) / Previous Close
    """
    returns_df = prices_df.pct_change().dropna()
    return returns_df

def align_data(stock_returns, index_returns):
    """Aligns stock returns and index returns on the same dates."""
    merged = stock_returns.join(index_returns[['close']].rename(columns={'close': 'NIFTY'}), how='inner')
    merged.dropna(inplace=True)
    
    aligned_stock_returns = merged.drop(columns=['NIFTY'])
    aligned_index_returns = merged['NIFTY']
    return aligned_stock_returns, aligned_index_returns
