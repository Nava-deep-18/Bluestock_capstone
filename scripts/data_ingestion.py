import pandas as pd
import os
import glob

print("--- Data Ingestion ---")
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
        print(f"\n======================================")
        print(f"Dataset: {filename}")
        print(f"Shape: {df.shape}")
        print(f"Dtypes:\n{df.dtypes}")
        print(f"Head:\n{df.head(3)}")
    except Exception as e:
        print(f"Error loading {filename}: {e}")
