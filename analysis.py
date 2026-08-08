import os
import pandas as pd
from utils import load_and_merge_stocks, load_index, compute_daily_returns, align_data
from portfolio import (compute_statistics, min_variance_portfolio, 
                       value_weighted_portfolio, price_weighted_portfolio, 
                       portfolio_performance)
from capm import compute_capm
from charts import (plot_price_volume, plot_portfolio_comparison, 
                    plot_risk_return, plot_correlation_heatmap)
from excel_writer import write_excel
from config import OUTPUT_DIR, CHARTS_DIR

def main():
    print("Starting Finance Assignment Automation...")
    
    # 1. Ensure output directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CHARTS_DIR, exist_ok=True)
    
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
    
    # 7. CAPM (Task 7)
    print("Computing CAPM...")
    capm_df = compute_capm(stats, index_returns)
    
    # 8. Charts (Task 6 & Others)
    print("Generating charts...")
    chart_paths = plot_price_volume(all_data)
    p_comp_path = plot_portfolio_comparison(port_perf)
    rr_path = plot_risk_return(stats)
    corr_path = plot_correlation_heatmap(stock_returns)
    
    # 9. Excel Writing and Bond Analysis (Task 8 & 9)
    print("Writing to Excel and analyzing bonds...")
    write_excel(
        all_data, close_prices, stock_returns, stats, 
        port_weights, port_perf, capm_df, 
        chart_paths, p_comp_path, rr_path, corr_path
    )
    
    print("Automation complete.")

if __name__ == "__main__":
    main()
