import pandas as pd
import sqlite3
from pathlib import Path

def setup_database():
    project_dir = Path(__file__).parent.parent
    db_dir = project_dir / 'data' / 'db'
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / 'bluestock_mf.db'
    sql_schema_path = project_dir / 'sql' / 'schema.sql'
    processed_dir = project_dir / 'data' / 'processed'

    # Mapping of cleaned CSV files to their respective database tables
    file_to_table_map = {
        'clean_fund_master.csv': 'dim_fund',
        'clean_nav.csv': 'fact_nav',
        'clean_transactions.csv': 'fact_transactions',
        'clean_performance.csv': 'fact_performance',
        'clean_monthly_sip_inflows.csv': 'fact_sip_industry',
        'clean_portfolio_holdings.csv': 'fact_portfolio',
        'clean_aum_by_fund_house.csv': 'fact_aum',
        'clean_benchmark_indices.csv': 'fact_benchmark',
        'clean_category_inflows.csv': 'fact_category_inflows',
        'clean_industry_folio_count.csv': 'fact_folio_count'
    }
    
    # 1. Generate Schema DDL
    print("Generating schema.sql...")
    schema_statements = []
    
    # First, let's load sample data to generate schema
    for csv_file, table_name in file_to_table_map.items():
        csv_path = processed_dir / csv_file
        if csv_path.exists():
            df = pd.read_csv(csv_path, nrows=5)
            # Add primary/foreign keys manually for core tables if possible, but standard DDL is fine
            ddl = pd.io.sql.get_schema(df, table_name)
            schema_statements.append(f"-- Table: {table_name}\\n{ddl};\\n")
            
    with open(sql_schema_path, 'w') as f:
        f.write("\\n".join(schema_statements))
    print(f"Generated {sql_schema_path}")

    # 2. Connect and Load Data
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    
    for csv_file, table_name in file_to_table_map.items():
        csv_path = processed_dir / csv_file
        if csv_path.exists():
            print(f"Loading {csv_file} into table '{table_name}'...")
            df = pd.read_csv(csv_path)
            
            # Use to_sql with if_exists='replace' to create table and insert data
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            
            # Verify rows
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            print(f"  -> Successfully loaded {row_count} rows into {table_name}")
        else:
            print(f"WARNING: {csv_file} not found in processed folder. Skipping.")

    # Create explicit indices for performance as requested in design
    try:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_nav_amfi_date ON fact_nav (amfi_code, date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_trans_amfi_date ON fact_transactions (amfi_code, transaction_date)")
        print("Created performance indices.")
    except Exception as e:
        print(f"Error creating indices: {e}")

    conn.commit()
    conn.close()
    print("\\nDatabase loading complete!")

if __name__ == '__main__':
    setup_database()
