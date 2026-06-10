import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect('data/db/bluestock_mf.db')
query = "SELECT date, nav FROM fact_nav WHERE amfi_code = '120504' ORDER BY date ASC"  # Assuming 120504 is SBI Bluechip
df = pd.read_sql(query, conn)
df['date'] = pd.to_datetime(df['date'], dayfirst=True, format='mixed', errors='coerce')
df = df.dropna().sort_values('date')
df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
df['daily_return'] = df['nav'].pct_change()
mu = df['daily_return'].mean()
sigma = df['daily_return'].std()
print(f"Count: {len(df)}")
print(f"Mu: {mu}")
print(f"Sigma: {sigma}")
print(f"Latest NAV: {df['nav'].iloc[-1]}")

# Try 5 years compounded
simulated = np.random.normal(mu, sigma, (1260, 500))
paths = np.zeros_like(simulated)
paths[0] = df['nav'].iloc[-1] * (1 + simulated[0])
for t in range(1, 1260):
    paths[t] = paths[t-1] * (1 + simulated[t])
print(f"Max path: {np.max(paths)}")
print(f"95th: {np.percentile(paths, 95)}")
