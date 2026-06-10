import sqlite3
import pandas as pd
conn = sqlite3.connect('data/db/bluestock_mf.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
