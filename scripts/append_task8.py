import nbformat as nbf
from pathlib import Path

nb_path = Path('../notebooks/04_performance_analytics.ipynb')
nb = nbf.read(nb_path, as_version=4)

md8 = """## Task 8: Benchmark Comparison Chart & Tracking Error
*Note: We must normalize the NAV and Index values to start at 100 for a true comparison. If we didn't normalize, the Nifty indices (values over 20,000) would completely squash the mutual fund NAVs into indistinguishable flat lines at the bottom of the chart!*
"""
code8 = """import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

data_dir = Path('../data/processed')

# 1. Identify Top 5 Funds
scorecard = pd.read_csv(data_dir / 'fund_scorecard.csv')
top_5_funds = scorecard.head(5)['amfi_code'].tolist()
fund_master = pd.read_csv(data_dir / 'clean_fund_master.csv')
top_5_names = fund_master[fund_master['amfi_code'].isin(top_5_funds)].set_index('amfi_code')['scheme_name'].to_dict()

# 2. Get 3 Years of Data (End date is max date in our dataset)
nav_df = pd.read_csv(data_dir / 'returns_computed.csv', parse_dates=['date'])
end_date = nav_df['date'].max()
start_date = end_date - pd.DateOffset(years=3)

# Filter NAV for top 5 funds
nav_top5 = nav_df[(nav_df['amfi_code'].isin(top_5_funds)) & (nav_df['date'] >= start_date)].copy()

# Filter Benchmarks
benchmarks = pd.read_csv(data_dir / 'clean_benchmark_indices.csv', parse_dates=['date'])
nifty50 = benchmarks[(benchmarks['index_name'] == 'NIFTY50') & (benchmarks['date'] >= start_date)].copy()
nifty100 = benchmarks[(benchmarks['index_name'] == 'NIFTY100') & (benchmarks['date'] >= start_date)].copy()

plt.figure(figsize=(14, 8))

# Plot Nifty 50
if not nifty50.empty:
    nifty50 = nifty50.sort_values('date').reset_index(drop=True)
    nifty50['normalized'] = (nifty50['close_value'] / nifty50['close_value'].iloc[0]) * 100
    plt.plot(nifty50['date'], nifty50['normalized'], label='NIFTY 50', linewidth=3, color='black')

# Plot Nifty 100
if not nifty100.empty:
    nifty100 = nifty100.sort_values('date').reset_index(drop=True)
    nifty100['normalized'] = (nifty100['close_value'] / nifty100['close_value'].iloc[0]) * 100
    plt.plot(nifty100['date'], nifty100['normalized'], label='NIFTY 100', linewidth=3, color='grey', linestyle='--')

# Plot Top 5 Funds
for code in top_5_funds:
    fund_data = nav_top5[nav_top5['amfi_code'] == code].sort_values('date').reset_index(drop=True)
    if not fund_data.empty:
        fund_data['normalized'] = (fund_data['nav'] / fund_data['nav'].iloc[0]) * 100
        plt.plot(fund_data['date'], fund_data['normalized'], label=top_5_names[code])

plt.title('Top 5 Funds vs Benchmarks (3-Year Normalized Performance)')
plt.xlabel('Date')
plt.ylabel('Normalized Value (Base = 100)')
plt.legend()
plt.grid(True, alpha=0.3)

reports_dir = Path('../reports')
reports_dir.mkdir(parents=True, exist_ok=True)
chart_path = reports_dir / 'benchmark_chart.png'
plt.savefig(chart_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved benchmark chart to {chart_path}")

# 3. Compute Tracking Error against Nifty 100
print("\\n--- Tracking Error (vs NIFTY 100) ---")
# Nifty 100 daily returns over last 3 years
nifty100['daily_return'] = nifty100['close_value'].pct_change()

for code in top_5_funds:
    fund_data = nav_top5[nav_top5['amfi_code'] == code].sort_values('date')
    
    # Merge on date to align returns properly
    merged = pd.merge(fund_data[['date', 'daily_return']], nifty100[['date', 'daily_return']], on='date', suffixes=('_fund', '_bench')).dropna()
    
    # Tracking Error = std of difference * sqrt(252)
    diff = merged['daily_return_fund'] - merged['daily_return_bench']
    tracking_error = diff.std() * np.sqrt(252)
    
    print(f"{top_5_names[code]}: {tracking_error:.4f} (Annualised)")
"""

nb['cells'].append(nbf.v4.new_markdown_cell(md8))
nb['cells'].append(nbf.v4.new_code_cell(code8))

nbf.write(nb, nb_path)
print("Task 8 appended.")
