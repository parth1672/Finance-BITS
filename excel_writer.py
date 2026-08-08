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
    
    # Clean up column names for easy access later
    bond_df.columns = [str(c).strip() for c in bond_df.columns]
    
    rename_map = {
        'Category': 'Bond Category',
        'Bond Symbol': 'Bond Symbol',
        'Issuer': 'Issuer',
        'Issue Description': 'Issue Description',
        'Coupon Rate (%)': 'Coupon Rate (%)',
        'Face Value (₹)': 'Face Value (₹)',
        'Last Traded Price (₹)': 'Last Traded Price (₹)',
        'Current Yield (%)': 'Current Yield (%)',
        'Yield to Maturity (%)': 'Yield to Maturity (YTM %)',
        'Maturity Date': 'Maturity Date',
        'Approx. Years to Maturity': 'Remaining Maturity (Years)',
        'Open': 'Open Price (₹)',
        'High': 'High Price (₹)',
        'Low': 'Low Price (₹)',
        'Close': 'Close Price (₹)',
        'Volume': 'Volume Traded',
        'Value': 'Traded Value (₹)'
    }
    bond_df.rename(columns=rename_map, inplace=True)
    
    coupon_col = 'Coupon Rate (%)'
    ytm_col = 'Yield to Maturity (YTM %)'
    maturity_col = 'Remaining Maturity (Years)'
    sym_col = 'Bond Symbol'
    
    analysis_results = {}
    if coupon_col in bond_df.columns and sym_col in bond_df.columns:
        if bond_df[coupon_col].dtype == object:
            bond_df[coupon_col] = bond_df[coupon_col].astype(str).str.rstrip('%').astype(float)
        highest_coupon = bond_df.loc[bond_df[coupon_col].idxmax()]
        lowest_coupon = bond_df.loc[bond_df[coupon_col].idxmin()]
        analysis_results['Highest Coupon Rate'] = f"{highest_coupon[sym_col]} ({highest_coupon[coupon_col]:.2f}%)"
        analysis_results['Lowest Coupon Rate'] = f"{lowest_coupon[sym_col]} ({lowest_coupon[coupon_col]:.2f}%)"
        
    if ytm_col in bond_df.columns and sym_col in bond_df.columns:
        if bond_df[ytm_col].dtype == object:
             bond_df[ytm_col] = bond_df[ytm_col].astype(str).str.rstrip('%').astype(float)
        highest_ytm = bond_df.loc[bond_df[ytm_col].idxmax()]
        lowest_ytm = bond_df.loc[bond_df[ytm_col].idxmin()]
        analysis_results['Highest Yield to Maturity'] = f"{highest_ytm[sym_col]} ({highest_ytm[ytm_col]:.3f}%)"
        analysis_results['Lowest Yield to Maturity'] = f"{lowest_ytm[sym_col]} ({lowest_ytm[ytm_col]:.3f}%)"
        
    if maturity_col in bond_df.columns and sym_col in bond_df.columns:
        longest_maturity = bond_df.loc[bond_df[maturity_col].idxmax()]
        analysis_results['Longest Remaining Maturity'] = f"{longest_maturity[sym_col]} ({int(longest_maturity[maturity_col])} Years)"
        
    analysis_df = pd.DataFrame(list(analysis_results.items()), columns=['Category', 'Details'])
    
    return bond_df, analysis_df, sym_col, ytm_col


def format_worksheet(worksheet, df, workbook, include_index=True):
    """Applies professional formatting to a worksheet."""
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#D9E1F2',
        'border': 1
    })
    
    if include_index and df.index.name:
        worksheet.write(0, 0, str(df.index.name), header_format)
        
    col_offset = 1 if include_index else 0
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + col_offset, str(value), header_format)
        worksheet.set_column(col_num + col_offset, col_num + col_offset, 20)

    if include_index:
        worksheet.set_column(0, 0, 25)

    worksheet.freeze_panes(1, col_offset)
    worksheet.autofilter(0, 0, len(df), len(df.columns) + col_offset - 1)

def get_col_letter(col_idx):
    """Convert 0-indexed column number to Excel column letter."""
    result = ""
    col_idx += 1
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result

def write_excel(all_data, close_prices, volume_data, returns, stats, port_weights, port_perf, capm, analysis_texts, selected_stocks_df, exec_summary_data, cov_matrix, corr_matrix):
    """
    Writes all data and native Excel charts to the final Excel workbook.
    """
    bond_data, bond_analysis, bond_name_col, bond_ytm_col = analyze_bonds()
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    writer = pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter')
    workbook = writer.book
    
    percent_format = workbook.add_format({'num_format': '0.00%'})
    bold_format = workbook.add_format({'bold': True})
    
    # 00_Executive_Summary
    exec_sheet = workbook.add_worksheet('00_Executive_Summary')
    exec_sheet.set_column('A:B', 30)
    row = 0
    for k, v in exec_summary_data.items():
        exec_sheet.write(row, 0, k, bold_format)
        exec_sheet.write(row, 1, str(v))
        row += 1
    
    # 01_Selected_Stocks
    selected_stocks_df.to_excel(writer, sheet_name='01_Selected_Stocks', index=False)
    format_worksheet(writer.sheets['01_Selected_Stocks'], selected_stocks_df, workbook, include_index=False)
    writer.sheets['01_Selected_Stocks'].set_column('E:G', 20, percent_format)
    
    # 02_Daily_Prices
    close_prices.index.name = 'Date'
    close_prices.to_excel(writer, sheet_name='02_Daily_Prices')
    format_worksheet(writer.sheets['02_Daily_Prices'], close_prices, workbook)
    
    # Write volume data to a hidden sheet to source native charts
    volume_data.index.name = 'Date'
    volume_data.to_excel(writer, sheet_name='_Volume_Data')
    writer.sheets['_Volume_Data'].hide()
    
    # 03_Daily_Returns
    returns.index.name = 'Date'
    returns.to_excel(writer, sheet_name='03_Daily_Returns')
    format_worksheet(writer.sheets['03_Daily_Returns'], returns, workbook)
    writer.sheets['03_Daily_Returns'].set_column(1, len(returns.columns), 12, percent_format)
    
    # 04_Statistics
    stats.index.name = 'Stock'
    stats.to_excel(writer, sheet_name='04_Statistics')
    format_worksheet(writer.sheets['04_Statistics'], stats, workbook)
    writer.sheets['04_Statistics'].set_column('B:C', 15, percent_format)
    
    # Native Scatter Chart for Risk-Return
    scatter_chart = workbook.add_chart({'type': 'scatter', 'subtype': 'marker_only'})
    scatter_chart.add_series({
        'name': 'Risk vs Return',
        'categories': f"='04_Statistics'!$C$2:$C${len(stats) + 1}", # Standard Deviation (X)
        'values': f"='04_Statistics'!$B$2:$B${len(stats) + 1}",     # Mean Return (Y)
        'data_labels': {'series_name': True, 'position': 'above'}
    })
    scatter_chart.set_title({'name': 'Risk-Return Scatter Plot'})
    scatter_chart.set_x_axis({'name': 'Standard Deviation (Risk)'})
    scatter_chart.set_y_axis({'name': 'Mean Daily Return (Expected Return)'})
    writer.sheets['04_Statistics'].insert_chart('E2', scatter_chart, {'x_scale': 1.5, 'y_scale': 1.5})
    
    # 04A_Covariance_Matrix
    cov_matrix.index.name = 'Stock'
    cov_matrix.to_excel(writer, sheet_name='04A_Covariance_Matrix')
    format_worksheet(writer.sheets['04A_Covariance_Matrix'], cov_matrix, workbook)
    
    # 04B_Correlation_Matrix
    corr_matrix.index.name = 'Stock'
    corr_matrix.to_excel(writer, sheet_name='04B_Correlation_Matrix')
    format_worksheet(writer.sheets['04B_Correlation_Matrix'], corr_matrix, workbook)
    writer.sheets['04B_Correlation_Matrix'].set_column(1, len(corr_matrix.columns), 15, percent_format)
    writer.sheets['04B_Correlation_Matrix'].conditional_format(1, 1, len(corr_matrix), len(corr_matrix.columns), {
        'type': '3_color_scale',
        'min_color': '#F8696B',
        'mid_color': '#FFEB84',
        'max_color': '#63BE7B'
    })
    
    # 05_Portfolio_Weights
    print("\n--- Data Flow Trace in excel_writer.py ---")
    print("port_weights right before to_excel:\n", port_weights)
    print("------------------------------------------\n")
    port_weights.index.name = 'Stock'
    port_weights.to_excel(writer, sheet_name='05_Portfolio_Weights')
    format_worksheet(writer.sheets['05_Portfolio_Weights'], port_weights, workbook)
    writer.sheets['05_Portfolio_Weights'].set_column(1, len(port_weights.columns), 15, percent_format)
    
    # Native Column Chart for Portfolio Weights
    weight_chart = workbook.add_chart({'type': 'column'})
    for col_idx, port_name in enumerate(port_weights.columns):
        col_let = get_col_letter(col_idx + 1)
        weight_chart.add_series({
            'name': f"='05_Portfolio_Weights'!${col_let}$1",
            'categories': f"='05_Portfolio_Weights'!$A$2:$A${len(port_weights) + 1}",
            'values': f"='05_Portfolio_Weights'!${col_let}$2:${col_let}${len(port_weights) + 1}",
        })
    weight_chart.set_title({'name': 'Portfolio Weights Comparison'})
    weight_chart.set_y_axis({'name': 'Weight', 'num_format': '0%'})
    writer.sheets['05_Portfolio_Weights'].insert_chart('F2', weight_chart, {'x_scale': 1.5, 'y_scale': 1.5})
    
    # 06_Portfolio_Performance
    port_perf.index.name = 'Portfolio'
    port_perf.to_excel(writer, sheet_name='06_Portfolio_Performance')
    format_worksheet(writer.sheets['06_Portfolio_Performance'], port_perf, workbook)
    writer.sheets['06_Portfolio_Performance'].set_column(1, 4, 15, percent_format)
    
    # Native Column Chart for Portfolio Performance
    perf_chart = workbook.add_chart({'type': 'column'})
    perf_chart.add_series({
        'name': 'Annualized Return',
        'categories': f"='06_Portfolio_Performance'!$A$2:$A${len(port_perf) + 1}",
        'values': f"='06_Portfolio_Performance'!$C$2:$C${len(port_perf) + 1}",
    })
    perf_chart.add_series({
        'name': 'Annualized Risk',
        'categories': f"='06_Portfolio_Performance'!$A$2:$A${len(port_perf) + 1}",
        'values': f"='06_Portfolio_Performance'!$E$2:$E${len(port_perf) + 1}",
    })
    perf_chart.set_title({'name': 'Portfolio Performance Comparison'})
    perf_chart.set_y_axis({'name': 'Percentage', 'num_format': '0.0%'})
    writer.sheets['06_Portfolio_Performance'].insert_chart('H2', perf_chart, {'x_scale': 1.5, 'y_scale': 1.5})
    
    # 07_Price_Volume (Native Charts per stock)
    pv_sheet = workbook.add_worksheet('07_Price_Volume')
    pv_sheet.set_column('A:A', 80)
    
    row = 0
    for stock_idx, stock in enumerate(close_prices.columns):
        col_let = get_col_letter(stock_idx + 1)
        
        pv_sheet.write(row, 0, f"{stock} Price vs Date", bold_format)
        
        # Native Line Chart for Price
        price_chart = workbook.add_chart({'type': 'line'})
        price_chart.add_series({
            'name': f"='02_Daily_Prices'!${col_let}$1",
            'categories': f"='02_Daily_Prices'!$A$2:$A${len(close_prices) + 1}",
            'values': f"='02_Daily_Prices'!${col_let}$2:${col_let}${len(close_prices) + 1}",
            'line': {'color': 'blue'}
        })
        price_chart.set_title({'name': f"{stock} - Price vs Date"})
        price_chart.set_x_axis({'name': 'Date', 'date_axis': True})
        price_chart.set_y_axis({'name': 'Price (INR)'})
        pv_sheet.insert_chart(row + 1, 0, price_chart, {'x_scale': 1.2, 'y_scale': 1.2})
        
        # Native Column Chart for Volume
        volume_chart = workbook.add_chart({'type': 'column'})
        volume_chart.add_series({
            'name': f"='_Volume_Data'!${col_let}$1",
            'categories': f"='_Volume_Data'!$A$2:$A${len(volume_data) + 1}",
            'values': f"='_Volume_Data'!${col_let}$2:${col_let}${len(volume_data) + 1}",
            'fill': {'color': 'orange'}
        })
        volume_chart.set_title({'name': f"{stock} - Volume vs Date"})
        volume_chart.set_x_axis({'name': 'Date', 'date_axis': True})
        volume_chart.set_y_axis({'name': 'Volume'})
        pv_sheet.insert_chart(row + 1, 8, volume_chart, {'x_scale': 1.2, 'y_scale': 1.2})
        
        # Write analysis text
        if stock in analysis_texts:
            pv_sheet.write(row + 16, 0, analysis_texts[stock])
            
        row += 18
        
    # 08_CAPM
    capm.index.name = 'Stock'
    capm.to_excel(writer, sheet_name='08_CAPM')
    format_worksheet(writer.sheets['08_CAPM'], capm, workbook)
    writer.sheets['08_CAPM'].set_column('B:B', 15, percent_format)
    writer.sheets['08_CAPM'].set_column('D:F', 15, percent_format)
    
    # Native Column Chart for CAPM Expected Return
    capm_chart = workbook.add_chart({'type': 'column'})
    capm_chart.add_series({
        'name': 'Expected Return (CAPM)',
        'categories': f"='08_CAPM'!$A$2:$A${len(capm) + 1}",
        'values': f"='08_CAPM'!$D$2:$D${len(capm) + 1}",
    })
    capm_chart.set_title({'name': 'CAPM Expected Returns'})
    capm_chart.set_y_axis({'name': 'Expected Return', 'num_format': '0.0%'})
    writer.sheets['08_CAPM'].insert_chart('H2', capm_chart, {'x_scale': 1.5, 'y_scale': 1.5})
    
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
        
        # Native Column Chart for Bond Yield Comparison sourced from 09_Bond_Data
        if bond_ytm_col and bond_name_col:
            ytm_col_idx = bond_data.columns.get_loc(bond_ytm_col)
            name_col_idx = bond_data.columns.get_loc(bond_name_col)
            y_let = get_col_letter(ytm_col_idx)
            n_let = get_col_letter(name_col_idx)
            
            bond_chart = workbook.add_chart({'type': 'column'})
            bond_chart.add_series({
                'name': 'Yield to Maturity (YTM %)',
                'categories': f"='09_Bond_Data'!${n_let}$2:${n_let}${len(bond_data) + 1}",
                'values': f"='09_Bond_Data'!${y_let}$2:${y_let}${len(bond_data) + 1}",
            })
            bond_chart.set_title({'name': 'Yield to Maturity (YTM) Comparison'})
            bond_chart.set_y_axis({'name': 'YTM (%)'})
            writer.sheets['10_Bond_Analysis'].insert_chart('D2', bond_chart, {'x_scale': 1.5, 'y_scale': 1.5})
            
    else:
        workbook.add_worksheet('10_Bond_Analysis').write('A1', 'Bond Analysis Not Available')
        
    # 11_References
    ref_sheet = workbook.add_worksheet('11_References')
    ref_sheet.set_column('A:A', 40)
    ref_sheet.write('A1', 'References', bold_format)
    references = [
        "NSE India",
        "RBI Retail Direct",
        "Angel One Historical API",
        "SEBI YTM Calculator"
    ]
    for i, ref in enumerate(references, start=2):
        ref_sheet.write(f'A{i}', ref)
    
    writer.close()
    print(f"Workbook successfully saved to {OUTPUT_FILE}")
