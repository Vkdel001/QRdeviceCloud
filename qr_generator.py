import requests
import qrcode
from PIL import Image

def generate_payment_qr(output_filename="payment_qr.jpg"):
    """Generate 320x480 JPG QR code from ZwennPay API"""
    
    # ZwennPay API payload
    payload = {
        "MerchantId": 56,
        "SetTransactionAmount": True,
        "TransactionAmount": "200",
        "SetConvenienceIndicatorTip": False,
        "ConvenienceIndicatorTip": 0,
        "SetConvenienceFeeFixed": False,
        "ConvenienceFeeFixed": 0,
        "SetConvenienceFeePercentage": False,
        "ConvenienceFeePercentage": 0,
    }
    
    try:
        print("Calling ZwennPay API...")
        response = requests.post(
            "https://api.zwennpay.com:9425/api/v1.0/Common/GetMerchantQR",
            headers={"accept": "text/plain", "Content-Type": "application/json"},
            json=payload,
            timeout=20
        )
        
        response.raise_for_status()
        upi_data = response.text.strip()
        print(f"✓ Got UPI data: {len(upi_data)} characters")
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(upi_data)
        qr.make(fit=True)
        
        # Create QR image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Create exactly 320x480 canvas with white background
        canvas = Image.new('RGB', (320, 480), 'white')
        
        # Resize QR to fit nicely (280x280 centered)
        qr_size = 280
        qr_resized = qr_image.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        # Center the QR on canvas
        x_offset = (320 - qr_size) // 2  # 20 pixels from left/right
        y_offset = (480 - qr_size) // 2  # 100 pixels from top/bottom
        canvas.paste(qr_resized, (x_offset, y_offset))
        
        # Save as JPG (exactly like working images)
        canvas.save(output_filename, 'JPEG', quality=95)
        
        print(f"✓ QR saved as {output_filename}")
        print(f"✓ Image size: {canvas.size} (320x480)")
        
        return output_filename
        
    except Exception as e:
        print(f"✗ Error generating QR: {e}")
        return None

if __name__ == "__main__":
    result = generate_payment_qr()
    if result:
        print(f"\nQR code generated successfully: {result}")
        print("Now you can upload it using: python image_uploader.py")
    else:
        print("Failed to generate QR code")