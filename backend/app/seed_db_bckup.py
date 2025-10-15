# (Optional) standalone seeding script if you want to run it manually.
import sqlite3, os
DB_PATH = os.getenv("SQLITE_DB_PATH", "./data/sales.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT NOT NULL,
    product TEXT NOT NULL,
    revenue REAL NOT NULL,
    sale_date TEXT NOT NULL
);
""")
sample = [
    ('Texas', 'Laptop', 5000, '2024-08-01'),
    ('Texas', 'Phone', 3000, '2024-08-02'),
    ('California', 'Laptop', 8000, '2024-08-01'),
    ('New York', 'Tablet', 2500, '2024-09-05'),
    ('Texas', 'Tablet', 1200, '2024-09-07')
]
cur.executemany('INSERT INTO sales (region, product, revenue, sale_date) VALUES (?, ?, ?, ?)', sample)
conn.commit()
conn.close()
print("Seeded DB at", DB_PATH)
