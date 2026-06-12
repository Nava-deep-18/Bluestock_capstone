"""
Module: data_ingestion.py
Description: Component of the Bluestock Mutual Fund Analytics Capstone.
"""

import pandas as pd
import os
import glob

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, "data", "raw")
csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))

dfs = {}
for file in csv_files:
    filename = os.path.basename(file)
    try:
        df = pd.read_csv(file)
        dfs[filename] = df
    except Exception as e:
        print(f"Error loading {filename}: {e}")
