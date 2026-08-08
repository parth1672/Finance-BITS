import numpy as np
import pandas as pd
import scipy.optimize as sco
from config import STOCK_METADATA, TRADING_DAYS_PER_YEAR, RISK_FREE_RATE_ANNUAL

def compute_statistics(stock_returns, index_returns):
    """
    Computes Mean Daily Return, Standard Deviation, and Beta for each stock.
    Beta = Covariance(stock_return, nifty_return) / Variance(nifty_return)
    """
    stats = pd.DataFrame(index=stock_returns.columns)
    stats['Mean Daily Return'] = stock_returns.mean()
    stats['Standard Deviation'] = stock_returns.std()
    
    var_index = index_returns.var()
    betas = []
    for col in stock_returns.columns:
        cov = stock_returns[col].cov(index_returns)
        beta = cov / var_index
        betas.append(beta)
        
    stats['Beta'] = betas
    return stats

def min_variance_portfolio(returns):
    """
    Calculates weights for Minimum Variance Portfolio using scipy.optimize.
    Constraints: Weights sum to 1, Weights >= 0.
    """
    num_assets = len(returns.columns)
    cov_matrix = returns.cov().values
    
    print("\n--- Minimum Variance Optimization Debug ---")
    print(f"Covariance Matrix:\n{returns.cov()}")
    
    # Scale objective to prevent SciPy premature convergence on tiny gradients
    def portfolio_variance(weights):
        return np.dot(weights.T, np.dot(cov_matrix, weights))
        
    def scaled_portfolio_variance(weights):
        return portfolio_variance(weights) * 100000
    
    initial_weights = np.array([1/num_assets] * num_assets)
    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    print(f"Initial Weights: {initial_weights}")
    eq_var = portfolio_variance(initial_weights)
    print(f"Equal-Weight Portfolio Variance: {eq_var}")
    
    result = sco.minimize(scaled_portfolio_variance, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    
    print(f"Optimization Success: {result.success}")
    print(f"Optimization Message: {result.message}")
    
    if not result.success:
        raise ValueError(f"Optimization failed to converge: {result.message}")
        
    optimal_weights = result.x / np.sum(result.x) # Ensure it sums exactly to 1
    opt_var = portfolio_variance(optimal_weights)
    
    print(f"Optimized Weights: {optimal_weights}")
    print(f"Sum of Optimized Weights: {np.sum(optimal_weights)}")
    print(f"Optimized Portfolio Variance: {opt_var}")
    print("--------------------------------------------\n")
    
    assert opt_var <= eq_var + 1e-8, "Optimized variance is strictly worse than equal weights!"
    
    return pd.Series(optimal_weights, index=returns.columns)

def value_weighted_portfolio(stocks):
    """
    Calculates weights for Value Weighted Portfolio based on MarketCap.
    Weight = MarketCap / TotalMarketCap
    """
    caps = [STOCK_METADATA[stock]['MarketCap'] for stock in stocks]
    total_cap = sum(caps)
    weights = np.array([cap / total_cap for cap in caps])
    weights = weights / np.sum(weights) # Ensure it sums exactly to 1
    return pd.Series(weights, index=stocks)

def price_weighted_portfolio(latest_prices):
    """
    Calculates weights for Price Weighted Portfolio based on the latest prices.
    Weight = Latest Stock Price / Sum(Latest Prices)
    """
    total_price = latest_prices.sum()
    weights = latest_prices / total_price
    weights = weights / weights.sum() # Ensure it sums exactly to 1
    return pd.Series(weights, index=latest_prices.index)

def portfolio_performance(weights, returns):
    """
    Calculates Annualized Portfolio Return, Standard Deviation, and Sharpe Ratio.
    """
    mean_daily_returns = returns.mean()
    cov_matrix = returns.cov()
    
    # Portfolio daily metrics
    port_daily_return = np.sum(mean_daily_returns * weights)
    port_daily_std = np.sqrt(weights.T @ cov_matrix @ weights)
    
    # Annualize metrics
    port_annual_return = ((1 + port_daily_return) ** TRADING_DAYS_PER_YEAR) - 1
    port_annual_std = port_daily_std * np.sqrt(TRADING_DAYS_PER_YEAR)
    
    # Sharpe Ratio
    sharpe_ratio = (port_annual_return - RISK_FREE_RATE_ANNUAL) / port_annual_std
    
    return {
        'Daily Return': port_daily_return,
        'Annualized Return': port_annual_return,
        'Daily Risk': port_daily_std,
        'Annualized Risk': port_annual_std,
        'Sharpe Ratio': sharpe_ratio
    }
