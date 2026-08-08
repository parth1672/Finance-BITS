import pandas as pd
from config import TRADING_DAYS_PER_YEAR, RISK_FREE_RATE_ANNUAL

def compute_capm(stats_df, index_returns):
    """
    Annualize Daily Returns
    Expected Return = Rf + Beta * (Market Return - Rf)
    """
    capm_df = pd.DataFrame(index=stats_df.index)
    
    # Annualized Market Return
    annual_market_return = ((1 + index_returns.mean()) ** TRADING_DAYS_PER_YEAR) - 1
    
    # Annualize stock returns
    capm_df['Annualized Return'] = ((1 + stats_df['Mean Daily Return']) ** TRADING_DAYS_PER_YEAR) - 1
    
    # Expected Return from CAPM
    capm_df['Beta'] = stats_df['Beta']
    capm_df['Expected Return (CAPM)'] = RISK_FREE_RATE_ANNUAL + capm_df['Beta'] * (annual_market_return - RISK_FREE_RATE_ANNUAL)
    
    # You can also include market return and Rf in the output for reference
    capm_df['Market Return (Annual)'] = annual_market_return
    capm_df['Risk Free Rate'] = RISK_FREE_RATE_ANNUAL
    
    return capm_df
