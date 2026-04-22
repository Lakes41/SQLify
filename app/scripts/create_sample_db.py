import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_db(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        segment TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        price REAL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date DATETIME,
        total_amount REAL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    """)
    
    # Insert data
    segments = ["Retail", "Corporate", "SME"]
    categories = ["Electronics", "Clothing", "Home", "Garden"]
    
    # Customers
    for i in range(1, 21):
        cursor.execute("INSERT INTO customers (name, email, segment) VALUES (?, ?, ?)",
                       (f"Customer {i}", f"customer{i}@example.com", random.choice(segments)))
        
    # Products
    for i in range(1, 11):
        cursor.execute("INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
                       (f"Product {i}", random.choice(categories), round(random.uniform(10, 500), 2)))
        
    # Orders & Items
    start_date = datetime.now() - timedelta(days=365)
    for i in range(1, 101):
        cust_id = random.randint(1, 20)
        order_date = start_date + timedelta(days=random.randint(0, 364))
        
        # Order items
        total = 0
        num_items = random.randint(1, 5)
        order_items = []
        for _ in range(num_items):
            prod_id = random.randint(1, 10)
            qty = random.randint(1, 3)
            cursor.execute("SELECT price FROM products WHERE product_id = ?", (prod_id,))
            price = cursor.fetchone()[0]
            total += price * qty
            order_items.append((prod_id, qty, price))
            
        cursor.execute("INSERT INTO orders (customer_id, order_date, total_amount) VALUES (?, ?, ?)",
                       (cust_id, order_date.strftime("%Y-%m-%d %H:%M:%S"), round(total, 2)))
        order_id = cursor.lastrowid
        
        for prod_id, qty, price in order_items:
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                           (order_id, prod_id, qty, price))
            
    conn.commit()
    conn.close()
    print(f"Sample database created at {db_path}")

if __name__ == "__main__":
    print(f"Current working directory: {os.getcwd()}")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "sample_business.db")
    print(f"Target DB path: {os.path.abspath(db_path)}")
    create_db(os.path.abspath(db_path))
