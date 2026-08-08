import numpy as np

def generate_price_volume_analysis(all_data):
    """
    Generate textual analysis for every stock describing the relationship
    between trading volume and price movement, volatility, and spikes.
    """
    analysis_dict = {}
    
    for stock, df in all_data.items():
        daily_returns = df['close'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252)
        
        max_vol_idx = df['volume'].idxmax()
        max_vol_date = max_vol_idx.strftime('%Y-%m-%d')
        max_vol_val = df['volume'].max()
        
        price_trend = "upward" if df['close'].iloc[-1] > df['close'].iloc[0] else "downward"
        corr_pv = df['close'].corr(df['volume'])
        
        corr_desc = "positive" if corr_pv > 0.2 else "negative" if corr_pv < -0.2 else "weak"
        
        analysis_text = (
            f"Over the sample period, {stock} exhibited an overall {price_trend} price trend "
            f"with an annualized volatility of {volatility:.2%}. "
            f"The correlation between price and volume is {corr_desc} ({corr_pv:.2f}), indicating how investor participation aligns with price movements. "
            f"A notable unusual volume spike occurred on {max_vol_date} with {max_vol_val:,.0f} shares traded."
        )
        
        analysis_dict[stock] = analysis_text
        
    return analysis_dict
