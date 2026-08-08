import pandas as pd
import os
from config import OUTPUT_FILE, BOND_DIR

def analyze_bonds():
    """
    Reads Bond_Data.xlsx and performs basic analysis.
    """
    filepath = os.path.join(BOND_DIR, 'Bond_Data.xlsx')
    if not os.path.exists(filepath):
        return pd.DataFrame(), pd.DataFrame()
        
    bond_df = pd.read_excel(filepath)
    
    # Simple summary table
    summary_data = []
    
    def find_col(substring):
        for c in bond_df.columns:
            if substring.lower() in str(c).lower():
                return c
        return None
        
    coupon_col = find_col('coupon')
    ytm_col = find_col('yield') or find_col('ytm')
    maturity_col = find_col('maturity')
    name_col = find_col('name') or find_col('security') or bond_df.columns[0]
    
    analysis_results = {}
    if coupon_col:
        # Handle cases where coupon might be a string with % sign
        if bond_df[coupon_col].dtype == object:
            bond_df[coupon_col] = bond_df[coupon_col].astype(str).str.rstrip('%').astype(float)
        highest_coupon = bond_df.loc[bond_df[coupon_col].idxmax()]
        lowest_coupon = bond_df.loc[bond_df[coupon_col].idxmin()]
        analysis_results['Highest Coupon Rate'] = highest_coupon[name_col]
        analysis_results['Lowest Coupon Rate'] = lowest_coupon[name_col]
        
    if ytm_col:
        if bond_df[ytm_col].dtype == object:
             bond_df[ytm_col] = bond_df[ytm_col].astype(str).str.rstrip('%').astype(float)
        highest_ytm = bond_df.loc[bond_df[ytm_col].idxmax()]
        lowest_ytm = bond_df.loc[bond_df[ytm_col].idxmin()]
        analysis_results['Highest Yield to Maturity'] = highest_ytm[name_col]
        analysis_results['Lowest Yield to Maturity'] = lowest_ytm[name_col]
        
    if maturity_col:
        # Longest remaining maturity (max value in maturity column)
        longest_maturity = bond_df.loc[bond_df[maturity_col].idxmax()]
        analysis_results['Longest Remaining Maturity'] = longest_maturity[name_col]
        
    analysis_df = pd.DataFrame(list(analysis_results.items()), columns=['Metric', 'Security Name'])
    
    return bond_df, analysis_df


def format_worksheet(worksheet, df, workbook, include_index=True):
    """Applies professional formatting to a worksheet."""
    # Header format
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1
    })
    
    # Write headers
    if include_index and df.index.name:
        worksheet.write(0, 0, df.index.name, header_format)
        
    col_offset = 1 if include_index else 0
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + col_offset, str(value), header_format)
        worksheet.set_column(col_num + col_offset, col_num + col_offset, 15) # Auto width approximation

    # Freeze panes
    worksheet.freeze_panes(1, col_offset)
    
    # Filters
    worksheet.autofilter(0, 0, len(df), len(df.columns) + col_offset - 1)

def write_excel(all_data, close_prices, returns, stats, port_weights, port_perf, capm, chart_paths, p_comp_path, rr_path, corr_path):
    """
    Writes all data and charts to the final Excel workbook.
    """
    bond_data, bond_analysis = analyze_bonds()
    
    # Ensure output dir exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    writer = pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter')
    workbook = writer.book
    
    percent_format = workbook.add_format({'num_format': '0.00%'})
    
    # 01_Selected_Stocks
    stocks_list = pd.DataFrame({'Selected Stocks': list(all_data.keys())})
    stocks_list.to_excel(writer, sheet_name='01_Selected_Stocks', index=False)
    format_worksheet(writer.sheets['01_Selected_Stocks'], stocks_list, workbook, include_index=False)
    
    # 02_Daily_Prices
    close_prices.to_excel(writer, sheet_name='02_Daily_Prices')
    format_worksheet(writer.sheets['02_Daily_Prices'], close_prices, workbook)
    
    # 03_Daily_Returns
    returns.to_excel(writer, sheet_name='03_Daily_Returns')
    format_worksheet(writer.sheets['03_Daily_Returns'], returns, workbook)
    # Apply percentage format to returns
    writer.sheets['03_Daily_Returns'].set_column(1, len(returns.columns), 12, percent_format)
    
    # 04_Statistics
    stats.to_excel(writer, sheet_name='04_Statistics')
    format_worksheet(writer.sheets['04_Statistics'], stats, workbook)
    writer.sheets['04_Statistics'].set_column(1, 2, 15, percent_format) # Mean and Std Dev as percentage
    
    # 05_Portfolio_Weights
    port_weights.to_excel(writer, sheet_name='05_Portfolio_Weights')
    format_worksheet(writer.sheets['05_Portfolio_Weights'], port_weights, workbook)
    writer.sheets['05_Portfolio_Weights'].set_column(1, len(port_weights.columns), 15, percent_format)
    
    # 06_Portfolio_Performance
    port_perf.to_excel(writer, sheet_name='06_Portfolio_Performance')
    format_worksheet(writer.sheets['06_Portfolio_Performance'], port_perf, workbook)
    writer.sheets['06_Portfolio_Performance'].set_column(1, 2, 15, percent_format) # Return and StdDev
    # Insert portfolio comparison chart
    if os.path.exists(p_comp_path):
        writer.sheets['06_Portfolio_Performance'].insert_image('E2', p_comp_path)
    if os.path.exists(rr_path):
        writer.sheets['06_Portfolio_Performance'].insert_image('E30', rr_path)
    
    # 07_Price_Volume
    # We will just write a dummy text and insert all charts
    pv_sheet = workbook.add_worksheet('07_Price_Volume')
    row = 1
    for stock, paths in chart_paths.items():
        pv_sheet.write(row, 0, f"{stock} Charts")
        if os.path.exists(paths['price']):
            pv_sheet.insert_image(row+1, 0, paths['price'])
        if os.path.exists(paths['volume']):
            pv_sheet.insert_image(row+1, 10, paths['volume'])
        row += 30 # Move down for the next stock
        
    # 08_CAPM
    capm.to_excel(writer, sheet_name='08_CAPM')
    format_worksheet(writer.sheets['08_CAPM'], capm, workbook)
    writer.sheets['08_CAPM'].set_column(1, 1, 15, percent_format) # Annualized Return
    writer.sheets['08_CAPM'].set_column(3, 5, 15, percent_format) # CAPM Return, Market, Rf
    
    if os.path.exists(corr_path):
        writer.sheets['08_CAPM'].insert_image('H2', corr_path)
    
    # 09_Bond_Data
    if not bond_data.empty:
        bond_data.to_excel(writer, sheet_name='09_Bond_Data', index=False)
        format_worksheet(writer.sheets['09_Bond_Data'], bond_data, workbook, include_index=False)
    else:
        workbook.add_worksheet('09_Bond_Data').write('A1', 'Bond Data Not Found')
        
    # 10_Bond_Analysis
    if not bond_analysis.empty:
        bond_analysis.to_excel(writer, sheet_name='10_Bond_Analysis', index=False)
        format_worksheet(writer.sheets['10_Bond_Analysis'], bond_analysis, workbook, include_index=False)
    else:
        workbook.add_worksheet('10_Bond_Analysis').write('A1', 'Bond Analysis Not Available')
        
    # 11_References
    ref_sheet = workbook.add_worksheet('11_References')
    ref_sheet.write('A1', 'Data Sources')
    ref_sheet.write('A2', 'Historical stock and index data sourced from CSV files.')
    ref_sheet.write('A3', 'Bond data sourced from NSE/RBI Retail Direct (Bond_Data.xlsx).')
    
    writer.close()
    print(f"Workbook successfully saved to {OUTPUT_FILE}")
