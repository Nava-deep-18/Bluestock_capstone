"""
Master Run Script for Bluestock Mutual Fund Capstone.
This script serves as the single entry point to orchestrate the core ETL pipeline.
"""
import sys
from pathlib import Path

def main():
    print("===================================================")
    print(" BLUESTOCK MF CAPSTONE - CORE PIPELINE EXECUTION   ")
    print("===================================================\n")
    
    project_root = Path(__file__).resolve().parent
    scripts_dir = project_root / 'scripts'
    sys.path.append(str(scripts_dir))
    
    try:
        from etl_pipeline import run_pipeline as run_etl
        print("Triggering Core ETL Pipeline...")
        run_etl()
        print("\nSUCCESS: All core pipeline tasks completed successfully.")
    except Exception as e:
        print(f"CRITICAL ERROR: Pipeline execution failed. Details: {e}")

if __name__ == "__main__":
    main()
