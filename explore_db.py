import sqlite3
import sys

DB_PATH = "C:/Users/HP/Documents/Github/family-financial-os/family_financial.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]

print("=== TABLES ===")
for t in tables:
    print(t)

print("\n=== SCHEMA ===")
for t in tables:
    cursor.execute(f"PRAGMA table_info({t})")
    cols = cursor.fetchall()
    print(f"\n--- {t} ---")
    for c in cols:
        print(f"  {c[1]}: {c[2]}")

print("\n=== ROW COUNTS ===")
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"{t}: {count} rows")

conn.close()
