import os
import pandas as pd
from utils import load_and_merge_stocks, load_index, compute_daily_returns, align_data
from portfolio import (compute_statistics, min_variance_portfolio, 
                       value_weighted_portfolio, price_weighted_portfolio, 
                       portfolio_performance)
from capm import compute_capm
from charts import generate_price_volume_analysis
from excel_writer import write_excel
from config import OUTPUT_DIR, STOCK_METADATA

def main():
    print("Starting Finance Assignment Automation...")
    
    # 1. Ensure output directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 2. Load Data (Task 1)
    print("Loading data...")
    close_prices, volume_data, all_data = load_and_merge_stocks()
    index_data = load_index()
    
    # 3. Compute Returns (Task 2)
    print("Computing daily returns...")
    stock_returns_raw = compute_daily_returns(close_prices)
    index_returns_raw = compute_daily_returns(index_data[['close']])
    
    stock_returns, index_returns = align_data(stock_returns_raw, index_returns_raw)
    
    # 4. Compute Statistics (Task 3)
    print("Computing statistics...")
    stats = compute_statistics(stock_returns, index_returns)
    
    
    # 5. Portfolios (Task 4)
    print("Calculating portfolios...")
    cov_matrix = stock_returns.cov()
    corr_matrix = stock_returns.corr()
    
    min_var_weights = min_variance_portfolio(stock_returns)
    val_weight_weights = value_weighted_portfolio(stock_returns.columns)
    
    latest_prices = close_prices.iloc[-1]
    price_weight_weights = price_weighted_portfolio(latest_prices)
    
    port_weights = pd.DataFrame({
        'Minimum Variance': min_var_weights,
        'Value Weighted': val_weight_weights,
        'Price Weighted': price_weight_weights
    })
    
    # 6. Portfolio Performance (Task 5)
    print("Evaluating portfolio performance...")
    perf_min_var = portfolio_performance(min_var_weights, stock_returns)
    perf_val_weight = portfolio_performance(val_weight_weights, stock_returns)
    perf_price_weight = portfolio_performance(price_weight_weights, stock_returns)
    
    port_perf = pd.DataFrame({
        'Minimum Variance': perf_min_var,
        'Value Weighted': perf_val_weight,
        'Price Weighted': perf_price_weight
    }).T
    
    # Add Ranking
    port_perf['Ranking'] = port_perf['Sharpe Ratio'].rank(ascending=False).astype(int)
    
    # 7. CAPM (Task 7)
    print("Computing CAPM...")
    capm_df = compute_capm(stats, index_returns)
    
    # Selected Stocks Extended Data
    ss_data = []
    for stock in stock_returns.columns:
        meta = STOCK_METADATA[stock]
        ss_data.append({
            'Stock Name': meta['Name'],
            'NSE Symbol': meta['Symbol'],
            'Sector': meta['Sector'],
            'Market Capitalization': meta['MarketCap'],
            'Beta': stats.loc[stock, 'Beta'],
            'Mean Daily Return': stats.loc[stock, 'Mean Daily Return'],
            'Standard Deviation': stats.loc[stock, 'Standard Deviation']
        })
    selected_stocks_df = pd.DataFrame(ss_data)
    
    # Executive Summary Data
    exec_summary_data = {
        'Assignment Title': 'Finance Automation Assignment',
        'Student Name': '[Enter Student Name]',
        'Sample Period': f"{index_data.index.min().strftime('%Y-%m-%d')} to {index_data.index.max().strftime('%Y-%m-%d')}",
        'Selected Stocks': ', '.join(stock_returns.columns),
        'Portfolio with Highest Return': port_perf['Annualized Return'].idxmax(),
        'Portfolio with Lowest Risk': port_perf['Annualized Risk'].idxmin(),
        'Highest Beta Stock': stats['Beta'].idxmax(),
        'Highest Return Stock': stats['Mean Daily Return'].idxmax(),
        'Overall Conclusion': 'The Minimum Variance Portfolio successfully minimizes risk. Further details are explored in the performance and charts sections.'
    }
    
    # 8. Textual Analysis (Task 6)
    print("Generating textual analysis...")
    analysis_texts = generate_price_volume_analysis(all_data)
    
    # 9. Excel Writing and Bond Analysis (Task 8 & 9)
    print("Writing to Excel and building native charts...")
    write_excel(
        all_data, close_prices, volume_data, stock_returns, stats, 
        port_weights, port_perf, capm_df, 
        analysis_texts, selected_stocks_df, exec_summary_data, 
        cov_matrix, corr_matrix
    )
    
    print("Automation complete.")

if __name__ == "__main__":
    main()
