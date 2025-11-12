"""
Quick fix to add barcodes to existing products
"""
import sqlite3

conn = sqlite3.connect('body_soul.db')
cursor = conn.cursor()

print("Adding barcodes to products...")

# Update each product with its barcode
updates = [
    ('5901234123457', 'Body & Soul T-Shirt', 'M', 'Blue'),
    ('5901234123464', 'Body & Soul T-Shirt', 'L', 'Blue'),
    ('5901234123471', 'Body & Soul T-Shirt', 'M', 'Black'),
    ('5901234123488', 'Body & Soul Hoodie', 'M', 'Grey'),
    ('5901234123495', 'Body & Soul Hoodie', 'L', 'Grey'),
    ('5901234123501', 'Body & Soul Jeans', '32', 'Dark Blue'),
    ('5901234123518', 'Body & Soul Jeans', '34', 'Dark Blue'),
    ('5901234123525', 'Body & Soul Shorts', 'M', 'Khaki'),
    ('5901234123532', 'Body & Soul Cap', 'One Size', 'Black'),
    ('5901234123549', 'Body & Soul Socks', 'One Size', 'White'),
]

for barcode, name, size, color in updates:
    cursor.execute('''
        UPDATE products 
        SET barcode = ? 
        WHERE name = ? AND size = ? AND color = ?
    ''', (barcode, name, size, color))
    print(f"✓ {name} ({size}, {color}) → {barcode}")

conn.commit()
conn.close()

print("\nDone! Refresh your browser to see the barcodes.")
