import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'Data')
STOCKS_DIR = os.path.join(DATA_DIR, 'stocks')
INDEX_DIR = os.path.join(DATA_DIR, 'index')
BOND_DIR = os.path.join(DATA_DIR, 'bond')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
CHARTS_DIR = os.path.join(BASE_DIR, 'charts')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Finance_Assignment_Final.xlsx')

TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE_ANNUAL = 0.065

# Stock Metadata
STOCK_METADATA = {
    'BHARTIARTL': {'Name': 'Bharti Airtel Limited', 'Symbol': 'BHARTIARTL', 'Sector': 'Telecommunication', 'MarketCap': 800000},
    'HDFCBANK': {'Name': 'HDFC Bank Limited', 'Symbol': 'HDFCBANK', 'Sector': 'Financial Services', 'MarketCap': 1200000},
    'ICICIBANK': {'Name': 'ICICI Bank Limited', 'Symbol': 'ICICIBANK', 'Sector': 'Financial Services', 'MarketCap': 850000},
    'INFY': {'Name': 'Infosys Limited', 'Symbol': 'INFY', 'Sector': 'Information Technology', 'MarketCap': 600000},
    'RELIANCE': {'Name': 'Reliance Industries Limited', 'Symbol': 'RELIANCE', 'Sector': 'Energy/Conglomerate', 'MarketCap': 2000000},
    'TCS': {'Name': 'Tata Consultancy Services Limited', 'Symbol': 'TCS', 'Sector': 'Information Technology', 'MarketCap': 1400000}
}
