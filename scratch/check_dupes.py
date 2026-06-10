import sqlite3
import pandas as pd
conn = sqlite3.connect('data/db/bluestock_mf.db')
query = "SELECT * FROM fact_nav WHERE amfi_code = '119551' AND date = '2022-03-18'"
df = pd.read_sql(query, conn)
print(df)
