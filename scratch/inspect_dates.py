import sqlite3
import pandas as pd
conn = sqlite3.connect('data/db/bluestock_mf.db')
query = "SELECT date, nav FROM fact_nav LIMIT 5"
df = pd.read_sql(query, conn)
print("RAW DATA:")
print(df)
print("\nPARSED WITH dayfirst=True, format='mixed':")
print(pd.to_datetime(df['date'], dayfirst=True, format='mixed'))
print("\nPARSED WITH plain to_datetime:")
print(pd.to_datetime(df['date']))
