import sqlite3
import pandas as pd
conn = sqlite3.connect('data/db/bluestock_mf.db')
print("--- fact_sip_industry ---")
print(pd.read_sql("SELECT * FROM fact_sip_industry LIMIT 1", conn).columns)
print("--- fact_category_inflows ---")
print(pd.read_sql("SELECT * FROM fact_category_inflows LIMIT 1", conn).columns)
