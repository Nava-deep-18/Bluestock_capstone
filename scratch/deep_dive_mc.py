import sqlite3
import pandas as pd

conn = sqlite3.connect('data/db/bluestock_mf.db')

# Find the amfi code for SBI Bluechip
fund_df = pd.read_sql("SELECT scheme_name, amfi_code FROM dim_fund WHERE scheme_name LIKE '%SBI Bluechip%' LIMIT 1", conn)
print("Fund:", fund_df)
amfi_code = fund_df.iloc[0]['amfi_code']

query = f"SELECT date, nav FROM fact_nav WHERE amfi_code = '{amfi_code}' ORDER BY date ASC"
df = pd.read_sql(query, conn)
print("Raw count:", len(df))

# Mimic Streamlit EXACTLY
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date', 'nav']).sort_values('date')
df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
df = df.set_index('date').resample('B').ffill().reset_index()

df['daily_return'] = df['nav'].pct_change()
mu = df['daily_return'].mean()
sigma = df['daily_return'].std()

print("Mu:", mu)
print("Sigma:", sigma)
print("Max Daily Return:", df['daily_return'].max())
print("Min Daily Return:", df['daily_return'].min())

# Let's see the rows with the biggest returns
print("\nBiggest jumps:")
print(df.sort_values('daily_return', ascending=False).head(10))

print("\nBiggest drops:")
print(df.sort_values('daily_return', ascending=True).head(10))
