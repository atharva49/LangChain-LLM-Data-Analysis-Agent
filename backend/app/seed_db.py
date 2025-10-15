"""Seed the project's SQLite DB with a synthetic grocery dataset.

This script embeds a small dataset generator (uses Faker) and writes a
normalized SQLite database containing products, customers, transactions,
order_items, dimension tables and a fact table. It uses the environment
variable `SQLITE_DB_PATH` to locate the DB file (default: ./data/sales.db).

Run in PowerShell:

    python seed_db.py

Or set a custom path:

    $env:SQLITE_DB_PATH = 'data/grocery.db'; python seed_db.py
"""

import os
import sqlite3
import random
from pathlib import Path
from typing import List, Tuple, Iterable

try:
    from faker import Faker
except Exception as e:
    raise RuntimeError("Faker is required to run this seeder. Install with: pip install faker")


DB_PATH = os.getenv("SQLITE_DB_PATH", "./data/sales.db")


def generate_products(fake: Faker, n: int) -> List[dict]:
    categories = ["Produce", "Dairy", "Bakery", "Meat", "Seafood", "Frozen", "Beverages", "Snacks", "Household", "Personal Care"]
    products = []
    for i in range(1, n + 1):
        products.append({
            "product_id": i,
            "sku": f"SKU{i:05d}",
            "name": fake.unique.word().capitalize(),
            "category": random.choice(categories),
            "price": round(random.uniform(0.5, 50.0), 2),
        })
    return products


def generate_customers(fake: Faker, n: int) -> List[dict]:
    customers = []
    for i in range(1, n + 1):
        p = fake.simple_profile()
        customers.append({
            "customer_id": i,
            "name": p.get("name"),
            "username": p.get("username"),
            "email": p.get("mail"),
            "birthdate": str(p.get("birthdate")),
            "address": fake.address().replace("\n", ", "),
            "phone": fake.phone_number(),
        })
    return customers


def generate_stores(fake: Faker, n: int) -> List[dict]:
    stores = []
    for i in range(1, n + 1):
        stores.append({
            "store_id": i,
            "name": f"{fake.company()} Grocery",
            "address": fake.address().replace("\n", ", "),
            "city": fake.city(),
            "state": fake.state(),
            "zip": fake.postcode(),
            "region": random.choice(["North","South","East","West","Central"]),
        })
    return stores


def generate_transactions(fake: Faker, customers: List[dict], products: List[dict], n: int) -> Tuple[List[dict], List[dict]]:
    transactions = []
    order_items = []
    for i in range(1, n + 1):
        customer = random.choice(customers)
        num_distinct = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
        chosen = random.sample(products, k=num_distinct)
        items_repr = []
        total = 0.0
        total_qty = 0
        for prod in chosen:
            qty = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
            unit = prod["price"]
            line_total = round(unit * qty, 2)
            total += line_total
            total_qty += qty
            order_items.append({
                "transaction_id": i,
                "product_id": prod["product_id"],
                "quantity": qty,
                "unit_price": unit,
                "line_total": line_total,
            })
            items_repr.append(f"{prod['product_id']}:{qty}")

        transactions.append({
            "transaction_id": i,
            "customer_id": customer["customer_id"],
            "datetime": fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
            "num_items": total_qty,
            "total": round(total, 2),
            "items": "|".join(items_repr),
        })

    return transactions, order_items


def write_sqlite(db_path: str, products: Iterable[dict], customers: Iterable[dict], transactions: Iterable[dict], order_items: Iterable[dict], stores: Iterable[dict]):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    # base tables
    cur.execute("""CREATE TABLE IF NOT EXISTS products (product_id INTEGER PRIMARY KEY, sku TEXT, name TEXT, category TEXT, price REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS customers (customer_id INTEGER PRIMARY KEY, name TEXT, username TEXT, email TEXT, birthdate TEXT, address TEXT, phone TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS transactions (transaction_id INTEGER PRIMARY KEY, customer_id INTEGER, datetime TEXT, num_items INTEGER, total REAL, items TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS order_items (id INTEGER PRIMARY KEY AUTOINCREMENT, transaction_id INTEGER, product_id INTEGER, quantity INTEGER, unit_price REAL, line_total REAL)""")

    # dims and fact
    cur.execute("""CREATE TABLE IF NOT EXISTS dim_product (product_key INTEGER PRIMARY KEY, product_id INTEGER, sku TEXT, name TEXT, category TEXT, price REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS dim_customer (customer_key INTEGER PRIMARY KEY, customer_id INTEGER, name TEXT, username TEXT, email TEXT, birthdate TEXT, address TEXT, phone TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS dim_store (store_key INTEGER PRIMARY KEY, store_id INTEGER, name TEXT, address TEXT, city TEXT, state TEXT, zip TEXT, region TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS dim_date (date_key TEXT PRIMARY KEY, date_iso TEXT, year INTEGER, month INTEGER, day INTEGER, weekday INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS fact_sales (sale_id INTEGER PRIMARY KEY AUTOINCREMENT, transaction_id INTEGER, date_key TEXT, customer_key INTEGER, product_key INTEGER, store_key INTEGER, quantity INTEGER, unit_price REAL, line_total REAL)""")

    # inserts
    prod_vals = [(p['product_id'], p['sku'], p['name'], p['category'], p['price']) for p in products]
    cust_vals = [(c['customer_id'], c['name'], c['username'], c['email'], c['birthdate'], c['address'], c['phone']) for c in customers]
    trans_vals = [(t['transaction_id'], t['customer_id'], t['datetime'], t['num_items'], t['total'], t['items']) for t in transactions]
    order_vals = [(oi['transaction_id'], oi['product_id'], oi['quantity'], oi['unit_price'], oi['line_total']) for oi in order_items]

    cur.executemany("INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?)", prod_vals)
    cur.executemany("INSERT OR REPLACE INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)", cust_vals)
    cur.executemany("INSERT OR REPLACE INTO transactions VALUES (?, ?, ?, ?, ?, ?)", trans_vals)
    cur.executemany("INSERT INTO order_items (transaction_id, product_id, quantity, unit_price, line_total) VALUES (?, ?, ?, ?, ?)", order_vals)

    # populate dims
    dim_prod = [(p['product_id'], p['product_id'], p['sku'], p['name'], p['category'], p['price']) for p in products]
    dim_cust = [(c['customer_id'], c['customer_id'], c['name'], c['username'], c['email'], c['birthdate'], c['address'], c['phone']) for c in customers]
    cur.executemany("INSERT OR REPLACE INTO dim_product VALUES (?, ?, ?, ?, ?, ?)", dim_prod)
    cur.executemany("INSERT OR REPLACE INTO dim_customer VALUES (?, ?, ?, ?, ?, ?, ?, ?)", dim_cust)

    # stores
    store_rows = []
    for s in stores:
        store_rows.append((s['store_id'], s['store_id'], s['name'], s['address'], s['city'], s['state'], s['zip'], s['region']))
    cur.executemany("INSERT OR REPLACE INTO dim_store VALUES (?, ?, ?, ?, ?, ?, ?, ?)", store_rows)

    # dates
    date_map = {}
    for t in transactions:
        iso = t['datetime']
        date_only = iso.split('T')[0]
        if date_only not in date_map:
            parts = date_only.split('-')
            year = int(parts[0]) if len(parts) > 0 else 0
            month = int(parts[1]) if len(parts) > 1 else 0
            day = int(parts[2]) if len(parts) > 2 else 0
            weekday = random.randint(0, 6)
            date_map[date_only] = (date_only, iso, year, month, day, weekday)
    cur.executemany("INSERT OR REPLACE INTO dim_date VALUES (?, ?, ?, ?, ?, ?)", list(date_map.values()))

    # fact rows (one per order_item)
    fact_rows = []
    for oi in order_items:
        tx = next((t for t in transactions if t['transaction_id'] == oi['transaction_id']), None)
        if not tx:
            continue
        date_key = tx['datetime'].split('T')[0]
        # assign random store
        sk = random.choice(store_rows)[0]
        fact_rows.append((oi['transaction_id'], date_key, oi['transaction_id'], oi['product_id'], sk, oi['quantity'], oi['unit_price'], oi['line_total']))

    cur.executemany("INSERT INTO fact_sales (transaction_id, date_key, customer_key, product_key, store_key, quantity, unit_price, line_total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", fact_rows)

    conn.commit()
    conn.close()


def seed_main():
    fake = Faker()
    Faker.seed(0)
    random.seed(0)

    num_products = int(os.getenv('SEED_NUM_PRODUCTS', '100'))
    num_customers = int(os.getenv('SEED_NUM_CUSTOMERS', '200'))
    num_transactions = int(os.getenv('SEED_NUM_TRANSACTIONS', '1000'))
    num_stores = int(os.getenv('SEED_NUM_STORES', '10'))

    products = generate_products(fake, num_products)
    customers = generate_customers(fake, num_customers)
    transactions, order_items = generate_transactions(fake, customers, products, num_transactions)
    stores = generate_stores(fake, num_stores)

    write_sqlite(DB_PATH, products, customers, transactions, order_items, stores)
    print("Seeded DB at", DB_PATH)


if __name__ == '__main__':
    seed_main()
