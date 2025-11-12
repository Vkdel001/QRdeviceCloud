"""
Database migration script to add new columns for enhanced POS
"""
import sqlite3

def migrate_database():
    """Add new columns to existing database"""
    print("="*60)
    print("Database Migration - Enhanced POS")
    print("="*60)
    
    conn = sqlite3.connect('body_soul.db')
    cursor = conn.cursor()
    
    # Check existing columns in transactions table
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"\nExisting columns in transactions: {columns}")
    
    # Add missing columns to transactions table
    if 'receipt_number' not in columns:
        print("Adding receipt_number column...")
        cursor.execute('ALTER TABLE transactions ADD COLUMN receipt_number TEXT')
        print("✓ Added receipt_number")
    
    if 'subtotal' not in columns:
        print("Adding subtotal column...")
        cursor.execute('ALTER TABLE transactions ADD COLUMN subtotal REAL DEFAULT 0')
        print("✓ Added subtotal")
    
    if 'vat_amount' not in columns:
        print("Adding vat_amount column...")
        cursor.execute('ALTER TABLE transactions ADD COLUMN vat_amount REAL DEFAULT 0')
        print("✓ Added vat_amount")
    
    if 'payment_method' not in columns:
        print("Adding payment_method column...")
        cursor.execute('ALTER TABLE transactions ADD COLUMN payment_method TEXT DEFAULT "QR"')
        print("✓ Added payment_method")
    
    # Check existing columns in products table
    cursor.execute("PRAGMA table_info(products)")
    columns = [column[1] for column in cursor.fetchall()]
    print(f"\nExisting columns in products: {columns}")
    
    # Add barcode column to products table if missing
    if 'barcode' not in columns:
        print("Adding barcode column...")
        cursor.execute('ALTER TABLE products ADD COLUMN barcode TEXT')
        print("✓ Added barcode")
        
        # Add barcodes to existing products
        print("\nAdding barcodes to existing products...")
        cursor.execute('SELECT id, name, size, color FROM products')
        products = cursor.fetchall()
        
        barcode_map = {
            ('Body & Soul T-Shirt', 'M', 'Blue'): '5901234123457',
            ('Body & Soul T-Shirt', 'L', 'Blue'): '5901234123464',
            ('Body & Soul T-Shirt', 'M', 'Black'): '5901234123471',
            ('Body & Soul Hoodie', 'M', 'Grey'): '5901234123488',
            ('Body & Soul Hoodie', 'L', 'Grey'): '5901234123495',
            ('Body & Soul Jeans', '32', 'Dark Blue'): '5901234123501',
            ('Body & Soul Jeans', '34', 'Dark Blue'): '5901234123518',
            ('Body & Soul Shorts', 'M', 'Khaki'): '5901234123525',
            ('Body & Soul Cap', 'One Size', 'Black'): '5901234123532',
            ('Body & Soul Socks', 'One Size', 'White'): '5901234123549',
        }
        
        for product in products:
            product_id, name, size, color = product
            key = (name, size, color)
            if key in barcode_map:
                barcode = barcode_map[key]
                cursor.execute('UPDATE products SET barcode = ? WHERE id = ?', (barcode, product_id))
                print(f"  ✓ {name} ({size}, {color}) → {barcode}")
    
    # Update existing transactions with receipt numbers
    cursor.execute('SELECT id FROM transactions WHERE receipt_number IS NULL ORDER BY id')
    transactions = cursor.fetchall()
    
    if transactions:
        print(f"\nUpdating {len(transactions)} existing transactions with receipt numbers...")
        for idx, (transaction_id,) in enumerate(transactions, 1):
            receipt_number = f"BS-{idx:06d}"
            cursor.execute('UPDATE transactions SET receipt_number = ? WHERE id = ?', 
                         (receipt_number, transaction_id))
            print(f"  ✓ Transaction {transaction_id} → {receipt_number}")
    
    # Calculate and update VAT for existing transactions
    cursor.execute('SELECT id, total_amount FROM transactions WHERE subtotal IS NULL OR subtotal = 0')
    transactions = cursor.fetchall()
    
    if transactions:
        print(f"\nCalculating VAT for {len(transactions)} existing transactions...")
        VAT_RATE = 0.15
        for transaction_id, total_amount in transactions:
            subtotal = total_amount / (1 + VAT_RATE)
            vat_amount = total_amount - subtotal
            cursor.execute('''
                UPDATE transactions 
                SET subtotal = ?, vat_amount = ? 
                WHERE id = ?
            ''', (subtotal, vat_amount, transaction_id))
            print(f"  ✓ Transaction {transaction_id}: Total {total_amount:.2f} = Subtotal {subtotal:.2f} + VAT {vat_amount:.2f}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("Migration completed successfully!")
    print("="*60)
    print("\nYou can now run: python body_soul_pos_enhanced.py")
    print("="*60)

if __name__ == '__main__':
    try:
        migrate_database()
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print("\nIf you continue to have issues, you can:")
        print("1. Backup body_soul.db")
        print("2. Delete body_soul.db")
        print("3. Run python body_soul_pos_enhanced.py (will create fresh database)")
