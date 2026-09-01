import sqlite3
from pathlib import Path

db = Path(r'C:\Users\HP\Documents\Github\family-financial-os\family_financial.db')
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT id, start_date, end_date FROM debts LIMIT 5')
for r in cur.fetchall():
    print('debt_dates', repr(r[1]), repr(r[2]))
cur.execute('SELECT id, due_date, recommended_date, cutoff_date FROM financial_events LIMIT 5')
for r in cur.fetchall():
    print('event_dates', repr(r[1]), repr(r[2]), repr(r[3]))
conn.close()
