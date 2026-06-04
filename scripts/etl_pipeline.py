# As i had already experimented in notebooks based on that results this pipline was inspired
import os
import pandas as pd
from pathlib import Path
from load_database import setup_database

def clean_nav_data(raw_dir, processed_dir):
    """Extracts and cleans NAV history data."""
    print(" -> Cleaning NAV History...")
    nav_df = pd.read_csv(raw_dir / '02_nav_history.csv')
    nav_df['date'] = pd.to_datetime(nav_df['date'])
    nav_df = nav_df.drop_duplicates(subset=['amfi_code', 'date'])
    
    nav_df = nav_df.set_index('date')
    nav_filled = nav_df.groupby('amfi_code')['nav'].resample('D').ffill().reset_index()
    nav_filled = nav_filled.sort_values(by=['amfi_code', 'date'])
    nav_filled = nav_filled[nav_filled['nav'] > 0]
    
    nav_filled.to_csv(processed_dir / 'clean_nav.csv', index=False)

def clean_transaction_data(raw_dir, processed_dir):
    """Extracts and cleans investor transactions."""
    print(" -> Cleaning Investor Transactions...")
    tx_df = pd.read_csv(raw_dir / '08_investor_transactions.csv')
    tx_df['transaction_date'] = pd.to_datetime(tx_df['transaction_date'])
    tx_df['transaction_type'] = tx_df['transaction_type'].str.strip().str.title()
    tx_df['transaction_type'] = tx_df['transaction_type'].replace({'Sip': 'SIP'})
    tx_df = tx_df[tx_df['amount_inr'] > 0]
    tx_df['kyc_status'] = tx_df['kyc_status'].str.strip().str.title()
    
    tx_df.to_csv(processed_dir / 'clean_transactions.csv', index=False)

def clean_performance_data(raw_dir, processed_dir):
    """Extracts and cleans scheme performance metrics."""
    print(" -> Cleaning Scheme Performance...")
    perf_df = pd.read_csv(raw_dir / '07_scheme_performance.csv')
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct']
    for col in return_cols:
        perf_df[col] = pd.to_numeric(perf_df[col], errors='coerce')
    perf_df = perf_df.dropna(subset=return_cols)
    
    perf_df['sharpe_ratio'] = pd.to_numeric(perf_df['sharpe_ratio'], errors='coerce')
    perf_df['has_negative_sharpe'] = perf_df['sharpe_ratio'] < 0
    perf_df['expense_ratio_pct'] = pd.to_numeric(perf_df['expense_ratio_pct'], errors='coerce')
    
    valid_expense = (perf_df['expense_ratio_pct'] >= 0.1) & (perf_df['expense_ratio_pct'] <= 2.5)
    perf_df = perf_df[valid_expense]
    
    perf_df.to_csv(processed_dir / 'clean_performance.csv', index=False)

def clean_remaining_datasets(raw_dir, processed_dir):
    """Copies over the remaining clean datasets."""
    print(" -> Transferring remaining static datasets...")
    file_mapping = {
        '01_fund_master.csv': 'clean_fund_master.csv',
        '03_aum_by_fund_house.csv': 'clean_aum_by_fund_house.csv',
        '04_monthly_sip_inflows.csv': 'clean_monthly_sip_inflows.csv',
        '05_category_inflows.csv': 'clean_category_inflows.csv',
        '06_industry_folio_count.csv': 'clean_industry_folio_count.csv',
        '09_portfolio_holdings.csv': 'clean_portfolio_holdings.csv',
        '10_benchmark_indices.csv': 'clean_benchmark_indices.csv'
    }
    
    for raw_name, clean_name in file_mapping.items():
        raw_path = raw_dir / raw_name
        if raw_path.exists():
            temp_df = pd.read_csv(raw_path)
            temp_df.to_csv(processed_dir / clean_name, index=False)

def run_pipeline():
    """Master Orchestrator Function"""
    print("=== Starting Modular ETL Pipeline ===")
    
    project_dir = Path(__file__).resolve().parent.parent
    raw_dir = project_dir / 'data' / 'raw'
    processed_dir = project_dir / 'data' / 'processed'
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Phase 1: Transform (Clean the CSVs)
        print("\n[PHASE 1] Data Transformation")
        clean_nav_data(raw_dir, processed_dir)
        clean_transaction_data(raw_dir, processed_dir)
        clean_performance_data(raw_dir, processed_dir)
        clean_remaining_datasets(raw_dir, processed_dir)
        
        # Phase 2: Load (Execute imported database script)
        print("\n[PHASE 2] Database Loading")
        setup_database()  # This function handles the entire SQLAlchemy logic!
        
        print("\n=== ETL Pipeline Completed Successfully! ===")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Pipeline Failed: {str(e)}")

if __name__ == '__main__':
    run_pipeline()
