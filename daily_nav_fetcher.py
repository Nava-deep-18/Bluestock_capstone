"""
Bonus Scheduled ETL Pipeline for Bluestock Mutual Fund Capstone.
This script orchestrates the Daily Scheduled Pipeline (Bonus Task):
1. Fetches Live NAV data from mfapi.in
2. Cleans and merges it with historical data
3. Updates the SQLite Database
"""
import sys
from pathlib import Path

def main():
    print("=========================================================")
    print(" BLUESTOCK MF CAPSTONE - SCHEDULED BONUS PIPELINE (8 PM) ")
    print("=========================================================\n")
    
    # Define paths
    project_root = Path(__file__).resolve().parent
    scripts_dir = project_root / 'scripts'
    raw_dir = project_root / 'data' / 'raw'
    sys.path.append(str(scripts_dir))
    
    try:
        # Step 1: Live Data Fetch
        from live_nav_fetch import fetch_and_update_nav
        target_funds = ["119551", "120503", "118632", "119092", "120841"]
        fetch_and_update_nav(target_funds, raw_dir)
        
        print("\n---------------------------------------------------------")
        
        # Step 2 & 3: Transform and Load (ETL Engine)
        from etl_pipeline import run_pipeline as run_etl
        print("Triggering Core ETL Engine to process fresh data...\n")
        run_etl()
        
        print("\n=========================================================")
        print(" SUCCESS: Daily Bonus Pipeline Completed!")
        print(" The database has been successfully updated with live data.")
        print("=========================================================")
        
    except ImportError as e:
        print(f"CRITICAL ERROR: Could not find scripts. Details: {e}")
    except Exception as e:
        print(f"CRITICAL ERROR: Pipeline execution failed. Details: {e}")

if __name__ == "__main__":
    main()
