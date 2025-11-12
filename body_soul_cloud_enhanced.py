"""
Body & Soul POS - Cloud Service (Railway-Ready)
This service handles the web interface, database, and business logic.
ESP32 communication is delegated to the local service.
"""

from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
import json
import requests

app = Flask(__name__)

# Configuration
LOCAL_SERVICE_PORTS = [8080, 8081, 8082, 8083]  # Try multiple ports
LOCAL_SERVICE_URL = None  # Will be set when we find the working port
LOCAL_API_KEY = os.getenv('LOCAL_API_KEY', 'dev-key-12345')

def find_local_service():
    """Find which port the local service is running on"""
    global LOCAL_SERVICE_URL
    
    # If already found, return it
    if LOCAL_SERVICE_URL:
        return LOCAL_SERVICE_URL
    
    # Check environment variable first
    env_url = os.getenv('LOCAL_SERVICE_URL')
    if env_url:
        try:
            response = requests.get(f"{env_url}/health", timeout=2)
            if response.status_code == 200:
                LOCAL_SERVICE_URL = env_url
                return LOCAL_SERVICE_URL
        except:
            pass
    
    # Try each port
    for port in LOCAL_SERVICE_PORTS:
        try:
            test_url = f"http://localhost:{port}"
            response = requests.get(f"{test_url}/health", timeout=2)
            if response.status_code == 200:
                LOCAL_SERVICE_URL = test_url
                print(f"✓ Found local service on port {port}")
                return LOCAL_SERVICE_URL
        except:
            continue
    
    return None

# Database configuration - supports both SQLite (local) and PostgreSQL (cloud)
def get_database_url():
    """Get database URL with debug logging"""
    db_url = os.getenv('DATABASE_URL')
    print(f"DEBUG: DATABASE_URL = {db_url[:50] if db_url else 'None'}...")
    return db_url

DATABASE_URL = get_database_url()

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

def get_db_connection():
    """Get database connection - supports SQLite and PostgreSQL"""
    db_url = os.getenv('DATABASE_URL')  # Read fresh each time
    print(f"DEBUG: Connecting with DATABASE_URL present: {bool(db_url)}")
    if db_url and 'postgres' in db_url:
        # PostgreSQL for cloud deployment
        try:
            import psycopg2
            import psycopg2.extras
            # Fix Railway's postgres:// to postgresql://
            connection_url = db_url.replace('postgres://', 'postgresql://', 1)
            print(f"Connecting to PostgreSQL...")
            conn = psycopg2.connect(connection_url)
            print(f"✓ PostgreSQL connected")
            return conn, 'postgresql'
        except Exception as e:
            print(f"✗ PostgreSQL connection failed: {e}")
            print(f"Falling back to SQLite...")
            import sqlite3
            conn = sqlite3.connect('body_soul.db')
            conn.row_factory = sqlite3.Row
            return conn, 'sqlite'
    else:
        # SQLite for local development
        print(f"Using SQLite database")
        import sqlite3
        conn = sqlite3.connect('body_soul.db')
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def init_db():
    """Initialize database with sample Body and Soul products"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == 'postgresql':
        # PostgreSQL schema
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
    else:
        # SQLite schema
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
    
    # Insert sample products if table is empty
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    
    if count == 0:
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
        ''' if db_type == 'postgresql' else '''
            INSERT INTO products (name, category, price, size, color, stock, barcode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_products)
    
    conn.commit()
    conn.close()

def generate_receipt_number():
    """Generate unique receipt number"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT receipt_number FROM transactions ORDER BY id DESC LIMIT 1')
    last_receipt = cursor.fetchone()
    
    if last_receipt:
        last_num = int(last_receipt[0].split('-')[1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    conn.close()
    return f"BS-{new_num:06d}"

@app.route('/')
def index():
    """Main POS interface"""
    return render_template('pos_enhanced.html')

@app.route('/api/products')
def get_products():
    """Get all products"""
    conn, db_type = get_db_connection()
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
            'price': float(row[3]),
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
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = '%s' if db_type == 'postgresql' else '?'
    cursor.execute(f'''
        SELECT id, name, category, price, size, color, stock, barcode 
        FROM products 
        WHERE barcode = {placeholder} AND stock > 0
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
                'price': float(row[3]),
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
    """Generate payment QR via local service"""
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
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if db_type == 'postgresql' else '?'
        cursor.execute(f'''
            INSERT INTO transactions (receipt_number, total_amount, subtotal, vat_amount, items_json, payment_method)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (receipt_number, total_amount, subtotal, vat_amount, json.dumps(cart_items), 'QR'))
        
        if db_type == 'postgresql':
            cursor.execute('SELECT lastval()')
            transaction_id = cursor.fetchone()[0]
        else:
            transaction_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Call local service to generate and upload QR
        local_url = find_local_service()
        if not local_url:
            return jsonify({'error': 'Local payment device not found. Please ensure the local service is running.'}), 500
        
        try:
            local_response = requests.post(
                f"{local_url}/generate_qr",
                json={
                    'amount': total_amount,
                    'transaction_id': transaction_id,
                    'receipt_number': receipt_number
                },
                headers={'X-API-Key': LOCAL_API_KEY},
                timeout=30
            )
            
            if local_response.status_code == 200:
                result = local_response.json()
                if result.get('success'):
                    return jsonify({
                        'success': True,
                        'transaction_id': transaction_id,
                        'receipt_number': receipt_number,
                        'message': f'QR generated for MUR {total_amount:.2f}'
                    })
                else:
                    return jsonify({'error': result.get('error', 'Unknown error from local service')}), 500
            else:
                return jsonify({'error': f'Local service returned status {local_response.status_code}'}), 500
                
        except requests.exceptions.ConnectionError:
            return jsonify({'error': 'Cannot connect to local payment device. Please ensure the local service is running.'}), 500
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Timeout connecting to local payment device.'}), 500
        except Exception as e:
            return jsonify({'error': f'Error communicating with local device: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payment_complete', methods=['POST'])
def payment_complete():
    """Mark payment as complete"""
    try:
        data = request.json
        transaction_id = data.get('transaction_id')
        
        # Update transaction status
        conn, db_type = get_db_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if db_type == 'postgresql' else '?'
        cursor.execute(f'''
            UPDATE transactions 
            SET status = 'completed' 
            WHERE id = {placeholder}
        ''', (transaction_id,))
        conn.commit()
        conn.close()
        
        # Notify local service to restart rotation
        local_url = find_local_service()
        if local_url:
            try:
                requests.post(
                    f"{local_url}/payment_complete",
                    json={'transaction_id': transaction_id},
                    headers={'X-API-Key': LOCAL_API_KEY},
                    timeout=10
                )
            except:
                pass  # Don't fail if local service is offline
        
        return jsonify({'success': True, 'message': 'Payment completed'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/receipt/<int:transaction_id>')
def get_receipt(transaction_id):
    """Get receipt data for a transaction"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    placeholder = '%s' if db_type == 'postgresql' else '?'
    cursor.execute(f'''
        SELECT receipt_number, total_amount, subtotal, vat_amount, items_json, timestamp, payment_method
        FROM transactions 
        WHERE id = {placeholder}
    ''', (transaction_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'success': True,
            'receipt': {
                'receipt_number': row[0],
                'total_amount': float(row[1]),
                'subtotal': float(row[2]),
                'vat_amount': float(row[3]),
                'items': json.loads(row[4]),
                'timestamp': str(row[5]),
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

@app.route('/api/local_status')
def local_status():
    """Check if local service is online"""
    local_url = find_local_service()
    if not local_url:
        return jsonify({'status': 'offline', 'message': 'Local service not found on any port'})
    
    try:
        response = requests.get(
            f"{local_url}/health",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            data['url'] = local_url  # Include the URL we found
            return jsonify({'status': 'online', 'data': data})
        else:
            return jsonify({'status': 'error', 'message': f'Local service returned status {response.status_code}'})
    except requests.exceptions.ConnectionError:
        return jsonify({'status': 'offline', 'message': 'Cannot connect to local payment device'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({'status': 'healthy', 'service': 'Body & Soul Cloud POS'})

@app.route('/init_db')
def init_db_endpoint():
    """Initialize database - call this once after deployment"""
    try:
        init_db()
        return jsonify({'success': True, 'message': 'Database initialized successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    
    print("="*60)
    print("BODY & SOUL POS - CLOUD SERVICE (ENHANCED)")
    print("="*60)
    print("Features:")
    print("  ✓ Barcode Scanner Support")
    print("  ✓ Professional Receipts")
    print("  ✓ VAT Calculation")
    print("  ✓ Mauritius Compliance")
    print("  ✓ Cloud-Ready (Railway/Heroku)")
    print("="*60)
    print(f"POS Interface: http://localhost:{port}")
    print(f"Local Service Ports: {LOCAL_SERVICE_PORTS}")
    print("="*60)
    
    # Initialize database
    print("Initializing database...")
    try:
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
    
    print("="*60)
    print("Checking for local service...")
    local_url = find_local_service()
    if local_url:
        print(f"✓ Local service found: {local_url}")
    else:
        print("✗ Local service not found")
        print("  QR generation will not work until local service is started")
    print("="*60)
    
    app.run(debug=False, host='0.0.0.0', port=port)
