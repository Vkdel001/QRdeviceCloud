"""
Body & Soul POS - Local Service (ESP32 Handler)
This service runs on the store computer and handles ESP32 communication.
It provides a simple HTTP API for the cloud service to call.
"""

from flask import Flask, request, jsonify
import os
from datetime import datetime
import logging

app = Flask(__name__)

# Configuration
API_KEY = os.getenv('LOCAL_API_KEY', 'dev-key-12345')
COM_PORT = os.getenv('COM_PORT', 'COM3')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global ESP32 connection
global_uploader = None

def verify_api_key():
    """Verify API key from request"""
    api_key = request.headers.get('X-API-Key')
    if api_key != API_KEY:
        return False
    return True

def get_uploader():
    """Get or create persistent ESP32 connection"""
    global global_uploader
    if global_uploader is None:
        try:
            from image_uploader import ESP32ImageUploader
            global_uploader = ESP32ImageUploader()
            if not global_uploader.connect():
                logger.error("Failed to connect to ESP32")
                global_uploader = None
                return None
            logger.info("ESP32 connected successfully")
        except Exception as e:
            logger.error(f"Error creating uploader: {e}")
            global_uploader = None
            return None
    return global_uploader

@app.before_request
def check_api_key():
    """Check API key for all requests except health check"""
    if request.endpoint == 'health':
        return None
    
    if not verify_api_key():
        return jsonify({'error': 'Unauthorized'}), 401

@app.route('/health')
def health():
    """Health check endpoint"""
    uploader = get_uploader()
    device_status = 'connected' if uploader else 'disconnected'
    
    return jsonify({
        'status': 'online',
        'service': 'Body & Soul Local Service',
        'device': device_status,
        'com_port': COM_PORT,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    """Generate and upload QR code to ESP32"""
    try:
        data = request.json
        amount = data.get('amount')
        transaction_id = data.get('transaction_id')
        receipt_number = data.get('receipt_number')
        
        if not amount or amount <= 0:
            return jsonify({'error': 'Invalid amount'}), 400
        
        logger.info(f"Generating QR for MUR {amount} (Receipt: {receipt_number})")
        
        # Generate QR code
        from payment_qr import generate_payment_qr_with_amount
        qr_filename = generate_payment_qr_with_amount(amount)
        
        if not qr_filename:
            logger.error("Failed to generate QR code")
            return jsonify({'error': 'Failed to generate QR code'}), 500
        
        # Upload to ESP32
        uploader = get_uploader()
        if not uploader:
            logger.error("ESP32 not connected")
            return jsonify({'error': 'ESP32 device not connected'}), 500
        
        logger.info("Uploading QR to ESP32...")
        success = uploader.upload_image(qr_filename, 1, chunk_size=1024)
        
        if success:
            logger.info("QR uploaded successfully, stopping rotation")
            try:
                uploader.stop_rotation()
            except Exception as e:
                logger.warning(f"Could not stop rotation: {e}")
            
            # Clean up temp file
            try:
                os.remove(qr_filename)
            except:
                pass
            
            return jsonify({
                'success': True,
                'message': f'QR code uploaded for MUR {amount}',
                'transaction_id': transaction_id,
                'receipt_number': receipt_number
            })
        else:
            logger.error("Failed to upload QR to ESP32")
            return jsonify({'error': 'Failed to upload QR to device'}), 500
        
    except Exception as e:
        logger.error(f"Error in generate_qr: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/payment_complete', methods=['POST'])
def payment_complete():
    """Restart rotation after payment is complete"""
    try:
        data = request.json
        transaction_id = data.get('transaction_id')
        
        logger.info(f"Payment completed for transaction {transaction_id}")
        
        uploader = get_uploader()
        if uploader:
            try:
                uploader.start_rotation()
                logger.info("Rotation restarted")
            except Exception as e:
                logger.warning(f"Could not restart rotation: {e}")
        
        return jsonify({'success': True, 'message': 'Rotation restarted'})
        
    except Exception as e:
        logger.error(f"Error in payment_complete: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload_image', methods=['POST'])
def upload_image():
    """Upload custom image to ESP32"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        slot = request.form.get('slot', 2, type=int)
        
        # Save temporarily
        temp_path = f"temp_upload_{slot}.jpg"
        file.save(temp_path)
        
        # Upload to ESP32
        uploader = get_uploader()
        if not uploader:
            return jsonify({'error': 'ESP32 device not connected'}), 500
        
        success = uploader.upload_image(temp_path, slot, chunk_size=1024)
        
        # Clean up
        try:
            os.remove(temp_path)
        except:
            pass
        
        if success:
            return jsonify({'success': True, 'message': f'Image uploaded to slot {slot}'})
        else:
            return jsonify({'error': 'Failed to upload image'}), 500
        
    except Exception as e:
        logger.error(f"Error in upload_image: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/rotation/start', methods=['POST'])
def start_rotation():
    """Start image rotation"""
    try:
        uploader = get_uploader()
        if not uploader:
            return jsonify({'error': 'ESP32 device not connected'}), 500
        
        uploader.start_rotation()
        return jsonify({'success': True, 'message': 'Rotation started'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rotation/stop', methods=['POST'])
def stop_rotation():
    """Stop image rotation"""
    try:
        uploader = get_uploader()
        if not uploader:
            return jsonify({'error': 'ESP32 device not connected'}), 500
        
        uploader.stop_rotation()
        return jsonify({'success': True, 'message': 'Rotation stopped'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def find_available_port(start_port=8080, max_attempts=10):
    """Find an available port"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

if __name__ == '__main__':
    # Find available port
    port = find_available_port(8080)
    
    if not port:
        logger.error("Could not find available port")
        exit(1)
    
    print("="*60)
    print("BODY & SOUL LOCAL SERVICE (ENHANCED)")
    print("="*60)
    print("This service handles ESP32 communication")
    print("="*60)
    print(f"Service URL: http://localhost:{port}")
    print(f"COM Port: {COM_PORT}")
    print(f"API Key: {API_KEY[:10]}...")
    print("="*60)
    print("Connecting to ESP32...")
    print("="*60)
    
    # Test ESP32 connection
    uploader = get_uploader()
    if uploader:
        print("✓ ESP32 device connected successfully")
    else:
        print("✗ ESP32 device not found")
        print("  Service will start but QR generation will fail")
        print("  Please check:")
        print("  - ESP32 is connected to USB")
        print("  - COM port is correct")
        print("  - No other program is using the port")
    
    print("="*60)
    print("Local service is ready!")
    print("="*60)
    
    app.run(debug=False, host='0.0.0.0', port=port)
