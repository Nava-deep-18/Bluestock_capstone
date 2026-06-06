import pandas as pd
from pathlib import Path
import os

# Use relative path so the script is portable
base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / 'data' / 'processed'

# Load SIP data
sip_df = pd.read_csv(data_dir / 'clean_monthly_sip_inflows.csv')

# Load Benchmark data
benchmarks = pd.read_csv(data_dir / 'clean_benchmark_indices.csv', parse_dates=['date'])
nifty50 = benchmarks[benchmarks['index_name'] == 'NIFTY50'].copy()

# Create a YYYY-MM column in Nifty 50 to match SIP data
nifty50['month'] = nifty50['date'].dt.strftime('%Y-%m')

# Get the average Nifty 50 close value for each month
nifty_monthly = nifty50.groupby('month')['close_value'].mean().reset_index()
nifty_monthly.rename(columns={'close_value': 'nifty_50_avg'}, inplace=True)

# Merge them together
merged_df = pd.merge(sip_df, nifty_monthly, on='month', how='inner')

# Save for Power BI
merged_df.to_csv(data_dir / 'clean_sip_vs_nifty.csv', index=False)
print("Successfully generated clean_sip_vs_nifty.csv")
