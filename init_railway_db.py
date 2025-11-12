"""
One-time script to initialize Railway database
Run this locally to initialize the Railway database
"""
import os
import psycopg2

# Get DATABASE_URL from Railway
DATABASE_URL = input("Paste your DATABASE_URL from Railway: ")

# Connect to database
print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

print("Creating tables...")

# Create products table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        size TEXT,
        color TEXT,
        stock INTEGER DEFAULT 0,
        barcode TEXT UNIQUE
    )
''')

# Create transactions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        receipt_number TEXT UNIQUE NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        subtotal DECIMAL(10,2) NOT NULL,
        vat_amount DECIMAL(10,2) NOT NULL,
        items_json TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending',
        payment_method TEXT DEFAULT 'QR'
    )
''')

print("Inserting sample products...")

# Insert sample products
sample_products = [
    ('Body & Soul T-Shirt', 'Tops', 450.00, 'M', 'Blue', 25, '5901234123457'),
    ('Body & Soul T-Shirt', 'Tops', 450.00, 'L', 'Blue', 20, '5901234123464'),
    ('Body & Soul T-Shirt', 'Tops', 450.00, 'M', 'Black', 30, '5901234123471'),
    ('Body & Soul Hoodie', 'Tops', 890.00, 'M', 'Grey', 15, '5901234123488'),
    ('Body & Soul Hoodie', 'Tops', 890.00, 'L', 'Grey', 12, '5901234123495'),
    ('Body & Soul Jeans', 'Bottoms', 1250.00, '32', 'Dark Blue', 18, '5901234123501'),
    ('Body & Soul Jeans', 'Bottoms', 1250.00, '34', 'Dark Blue', 22, '5901234123518'),
    ('Body & Soul Shorts', 'Bottoms', 650.00, 'M', 'Khaki', 20, '5901234123525'),
    ('Body & Soul Cap', 'Accessories', 320.00, 'One Size', 'Black', 35, '5901234123532'),
    ('Body & Soul Socks', 'Accessories', 180.00, 'One Size', 'White', 50, '5901234123549')
]

cursor.executemany('''
    INSERT INTO products (name, category, price, size, color, stock, barcode)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (barcode) DO NOTHING
''', sample_products)

conn.commit()
print(f"✓ Inserted {cursor.rowcount} products")

# Verify
cursor.execute('SELECT COUNT(*) FROM products')
count = cursor.fetchone()[0]
print(f"✓ Total products in database: {count}")

conn.close()
print("✓ Database initialized successfully!")
