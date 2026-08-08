import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'Data')
STOCKS_DIR = os.path.join(DATA_DIR, 'stocks')
INDEX_DIR = os.path.join(DATA_DIR, 'index')
BOND_DIR = os.path.join(DATA_DIR, 'bond')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
CHARTS_DIR = os.path.join(BASE_DIR, 'charts')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Finance_Assignment.xlsx')

TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE_ANNUAL = 0.065

# Market Capitalization in INR Crores for Value-Weighted Portfolio
MARKET_CAPS = {
    'BHARTIARTL': 800000,
    'HDFCBANK': 1200000,
    'ICICIBANK': 850000,
    'INFY': 600000,
    'RELIANCE': 2000000,
    'TCS': 1400000
}
