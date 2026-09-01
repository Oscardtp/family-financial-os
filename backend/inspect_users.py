import sqlite3
from pathlib import Path

db = Path(r'C:\Users\HP\Documents\Github\family-financial-os\family_financial.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT id, email, password_hash FROM users')
for r in cur.fetchall():
    print(r)
conn.close()
