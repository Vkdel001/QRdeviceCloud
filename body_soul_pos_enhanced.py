from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime
import json

app = Flask(__name__)

# Global persistent connection to ESP32
global_uploader = None

# Company details for receipts (Mauritius requirements)
COMPANY_INFO = {
    'name': 'Body & Soul Mauritius',
    'address': 'Royal Road, Port Louis, Mauritius',
    'phone': '+230 5XXX XXXX',
    'email': 'info@bodyandsoul.mu',
    'brn': 'C12345678',  # Business Registration Number
    'vat_number': 'V1234567',  # VAT Registration Number
    'vat_rate': 0.15  # 15% VAT in Mauritius
}

def get_uploader():
    """Get or create persistent ESP32 connection"""
    global global_uploader
    if global_uploader is None:
        from image_uploader import ESP32ImageUploader
        global_uploader = ESP32ImageUploader()
        if not global_uploader.connect():
            global_uploader = None
            return None
    return global_uploader

# Initialize database
def init_db():
    """Initialize SQLite database with sample Body and Soul products"""
    conn = sqlite3.connect('body_soul.db')
    cursor = conn.cursor()
    
    # Create products table with barcode
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            size TEXT,
            color TEXT,
            stock INTEGER DEFAULT 0,
            barcode TEXT UNIQUE
        )
    ''')
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_number TEXT UNIQUE NOT NULL,
            total_amount REAL NOT NULL,
            subtotal REAL NOT NULL,
            vat_amount REAL NOT NULL,
            items_json TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            payment_method TEXT DEFAULT 'QR'
        )
    ''')
    
    # Check if barcode column exists, add if not
    cursor.execute("PRAGMA table_info(products)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'barcode' not in columns:
        cursor.execute('ALTER TABLE products ADD COLUMN barcode TEXT')
    
    # Insert sample Body and Soul products with barcodes
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
    
    # Check if products already exist
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO products (name, category, price, size, color, stock, barcode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_products)
    
    conn.commit()
    conn.close()

def generate_receipt_number():
    """Generate unique receipt number"""
    conn = sqlite3.connect('body_soul.db')
    cursor = conn.cursor()
    
    # Get last receipt number
    cursor.execute('SELECT receipt_number FROM transactions ORDER BY id DESC LIMIT 1')
    last_receipt = cursor.fetchone()
    
    if last_receipt:
        # Extract number and increment
        last_num = int(last_receipt[0].split('-')[1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    conn.close()
    return f"BS-{new_num:06d}"  # Format: BS-000001

@app.route('/')
def index():
    """Main POS interface"""
    return render_template('pos_enhanced.html')

@app.route('/api/products')
def get_products():
    """Get all products"""
    conn = sqlite3.connect('body_soul.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, category, price, size, color, stock, barcode 
        FROM products 
        WHERE stock > 0
        ORDER BY category, name
    ''')
    
    products = []
    for row in cursor.fetchall():
        products.append({
            'id': row[0],
            'name': row[1],
            'category': row[2],
            'price': row[3],
            'size': row[4],
            'color': row[5],
            'stock': row[6],
            'barcode': row[7]
        })
    
    conn.close()
    return jsonify(products)

@app.route('/api/product/barcode/<barcode>')
def get_product_by_barcode(barcode):
    """Get product by barcode"""
    conn = sqlite3.connect('body_soul.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, category, price, size, color, stock, barcode 
        FROM products 
        WHERE barcode = ? AND stock > 0
    ''', (barcode,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'success': True,
            'product': {
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'price': row[3],
                'size': row[4],
                'color': row[5],
                'stock': row[6],
                'barcode': row[7]
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Product not found'}), 404

@app.route('/api/generate_qr', methods=['POST'])
def generate_qr():
    """Generate payment QR"""
    try:
        data = request.json
        total_amount = data.get('amount')
        cart_items = data.get('items', [])
        
        if not total_amount or total_amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        # Calculate VAT
        vat_rate = COMPANY_INFO['vat_rate']
        subtotal = total_amount / (1 + vat_rate)
        vat_amount = total_amount - subtotal
        
        # Generate receipt number
        receipt_number = generate_receipt_number()
        
        # Save transaction to database
        conn = sqlite3.connect('body_soul.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (receipt_number, total_amount, subtotal, vat_amount, items_json, payment_method)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (receipt_number, total_amount, subtotal, vat_amount, json.dumps(cart_items), 'QR'))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Generate QR code using existing payment_qr module
        from payment_qr import generate_payment_qr_with_amount
        
        qr_filename = generate_payment_qr_with_amount(total_amount)
        if not qr_filename:
            return jsonify({'error': 'Failed to generate QR code'}), 500
        
        # Upload to ESP32
        uploader = get_uploader()
        if uploader:
            success = uploader.upload_image(qr_filename, 1, chunk_size=1024)
            if success:
                try:
                    uploader.stop_rotation()
                except:
                    pass
            
            # Clean up temp file
            try:
                os.remove(qr_filename)
            except:
                pass
        
        return jsonify({
            'success': True,
            'transaction_id': transaction_id,
            'receipt_number': receipt_number,
            'message': f'QR generated for MUR {total_amount:.2f}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payment_complete', methods=['POST'])
def payment_complete():
    """Mark payment as complete"""
    try:
        data = request.json
        transaction_id = data.get('transaction_id')
        
        # Update transaction status
        conn = sqlite3.connect('body_soul.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions 
            SET status = 'completed' 
            WHERE id = ?
        ''', (transaction_id,))
        conn.commit()
        conn.close()
        
        # Restart rotation
        uploader = get_uploader()
        if uploader:
            try:
                uploader.start_rotation()
            except:
                pass
        
        return jsonify({'success': True, 'message': 'Payment completed'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/receipt/<int:transaction_id>')
def get_receipt(transaction_id):
    """Get receipt data for a transaction"""
    conn = sqlite3.connect('body_soul.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT receipt_number, total_amount, subtotal, vat_amount, items_json, timestamp, payment_method
        FROM transactions 
        WHERE id = ?
    ''', (transaction_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'success': True,
            'receipt': {
                'receipt_number': row[0],
                'total_amount': row[1],
                'subtotal': row[2],
                'vat_amount': row[3],
                'items': json.loads(row[4]),
                'timestamp': row[5],
                'payment_method': row[6],
                'company': COMPANY_INFO
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Receipt not found'}), 404

@app.route('/api/company_info')
def get_company_info():
    """Get company information"""
    return jsonify(COMPANY_INFO)

if __name__ == '__main__':
    # Initialize database
    init_db()
    print("="*60)
    print("BODY & SOUL POS - ENHANCED VERSION")
    print("="*60)
    print("Features:")
    print("  ✓ Barcode Scanner Support")
    print("  ✓ Professional Receipts")
    print("  ✓ VAT Calculation")
    print("  ✓ Mauritius Compliance")
    print("="*60)
    print("POS Interface: http://localhost:5000")
    print("="*60)
    app.run(debug=True, host='0.0.0.0', port=5000)
