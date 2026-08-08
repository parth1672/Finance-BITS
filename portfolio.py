import numpy as np
import pandas as pd
import scipy.optimize as sco
from config import MARKET_CAPS, TRADING_DAYS_PER_YEAR, RISK_FREE_RATE_ANNUAL

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
    cov_matrix = returns.cov()
    
    def portfolio_variance(weights):
        return weights.T @ cov_matrix @ weights
    
    initial_weights = np.array([1/num_assets] * num_assets)
    bounds = tuple((0, 1) for _ in range(num_assets))
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    result = sco.minimize(portfolio_variance, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    
    return pd.Series(result.x, index=returns.columns)

def value_weighted_portfolio(stocks):
    """
    Calculates weights for Value Weighted Portfolio based on MarketCap.
    Weight = MarketCap / TotalMarketCap
    """
    caps = [MARKET_CAPS[stock] for stock in stocks]
    total_cap = sum(caps)
    weights = [cap / total_cap for cap in caps]
    return pd.Series(weights, index=stocks)

def price_weighted_portfolio(latest_prices):
    """
    Calculates weights for Price Weighted Portfolio based on the latest prices.
    Weight = Latest Stock Price / Sum(Latest Prices)
    """
    total_price = latest_prices.sum()
    weights = latest_prices / total_price
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
    port_annual_return = port_daily_return * TRADING_DAYS_PER_YEAR
    port_annual_std = port_daily_std * np.sqrt(TRADING_DAYS_PER_YEAR)
    
    # Sharpe Ratio
    sharpe_ratio = (port_annual_return - RISK_FREE_RATE_ANNUAL) / port_annual_std
    
    return {
        'Return': port_annual_return,
        'Standard Deviation': port_annual_std,
        'Sharpe Ratio': sharpe_ratio
    }
