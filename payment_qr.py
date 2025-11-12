import requests
import qrcode
from PIL import Image
from image_uploader import ESP32ImageUploader

def generate_payment_qr_with_amount(amount, output_filename="payment_qr.jpg"):
    """Generate 320x480 JPG QR code with custom amount"""
    
    # ZwennPay API payload with custom amount
    payload = {
        "MerchantId": 56,
        "SetTransactionAmount": True,
        "TransactionAmount": str(amount),  # Use custom amount
        "SetConvenienceIndicatorTip": False,
        "ConvenienceIndicatorTip": 0,
        "SetConvenienceFeeFixed": False,
        "ConvenienceFeeFixed": 0,
        "SetConvenienceFeePercentage": False,
        "ConvenienceFeePercentage": 0,
    }
    
    try:
        print(f"Generating QR for amount: MUR {amount}")
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
        
        # Resize QR to fit with space for text below (250x250)
        qr_size = 250
        qr_resized = qr_image.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        # Position QR higher to leave space for text
        x_offset = (320 - qr_size) // 2  # Center horizontally
        y_offset = 50  # Start from top with margin
        canvas.paste(qr_resized, (x_offset, y_offset))
        
        # Add amount text below QR
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(canvas)
        
        # Try to use a larger font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Amount text
        amount_text = f"Amount: MUR {amount}"
        
        # Get text size and center it
        bbox = draw.textbbox((0, 0), amount_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (320 - text_width) // 2
        text_y = y_offset + qr_size + 20  # 20 pixels below QR
        
        # Draw text in black
        draw.text((text_x, text_y), amount_text, fill='black', font=font)
        
        # Save as JPG with lower quality to reduce file size
        canvas.save(output_filename, 'JPEG', quality=70)
        print(f"✓ QR saved as {output_filename} (320x480)")
        
        return output_filename
        
    except Exception as e:
        print(f"✗ Error generating QR: {e}")
        return None

def upload_qr_to_device(qr_filename, slot=1, uploader=None):
    """Upload QR using existing uploader connection"""
    try:
        # Use existing uploader connection instead of creating new one
        if uploader is None:
            print("✗ No uploader connection provided")
            return False
        
        print(f"Uploading QR to slot {slot}...")
        
        # Use EXACT same method call as manual upload option 1
        # Manual does: uploader.upload_image(image_path, file_number, chunk_size)
        # where chunk_size = int(input("Enter chunk size (default 1024): ") or "1024")
        chunk_size = 1024  # Same default as manual
        
        if uploader.upload_image(qr_filename, slot, chunk_size):
            print(f"✓ QR uploaded successfully to slot {slot}")
            
            # Stop rotation so QR stays visible
            print("Stopping rotation to display QR...")
            print("(This may take a few seconds...)")
            try:
                uploader.stop_rotation()
                print("✓ Rotation stopped")
            except Exception as e:
                print(f"✓ Rotation command sent (QR still uploaded successfully)")
            
            print("✓ QR is now displayed for customer to scan and pay.")
            print("Device will stay on with QR visible.")
            
            # Wait for staff confirmation that payment is completed
            while True:
                try:
                    payment_done = input("\nPayment process completed? (Y/N): ").strip().upper()
                    if payment_done == 'Y':
                        print("Restarting rotation for next customer...")
                        uploader.start_rotation()
                        print("✓ Device ready for next customer")
                        break
                    elif payment_done == 'N':
                        print("QR still displayed. Waiting for payment...")
                        continue
                    else:
                        print("Please enter Y or N")
                        continue
                except KeyboardInterrupt:
                    print("\nOperation cancelled. Starting rotation...")
                    uploader.start_rotation()
                    break
            
            # Keep connection alive for next operations
            return True
        else:
            print("✗ Failed to upload QR")
            uploader.disconnect()
            return False
            
    except Exception as e:
        print(f"✗ Error uploading QR: {e}")
        return False

def main():
    """Main payment QR generator and uploader - Coffee Shop POS"""
    print("="*50)
    print("COFFEE SHOP PAYMENT QR SYSTEM")
    print("="*50)
    
    # Create one persistent connection for entire session
    print("Connecting to ESP32...")
    uploader = ESP32ImageUploader()
    if not uploader.connect():
        print("✗ Failed to connect to ESP32. Please check connection.")
        return
    
    print("✓ Connected to ESP32. Device is ready.")
    
    try:
        while True:  # Continuous loop for multiple customers
            # Get amount from user
            amount = input("\nEnter payment amount (or 'exit' to quit): ").strip()
            
            if amount.lower() == 'exit':
                print("Exiting payment system...")
                break
            
            # Validate amount
            try:
                float_amount = float(amount)
                if float_amount <= 0:
                    print("Amount must be greater than 0")
                    continue
            except ValueError:
                print("Invalid amount. Please enter a number.")
                continue
            
            print(f"\nProcessing payment QR for MUR {amount}...")
            
            # Step 1: Generate QR
            qr_filename = generate_payment_qr_with_amount(amount)
            if not qr_filename:
                print("Failed to generate QR code")
                continue
            
            # Step 2: Upload to ESP32 using persistent connection
            if upload_qr_to_device(qr_filename, slot=1, uploader=uploader):
                print(f"\n✓ SUCCESS! Payment QR for MUR {amount} is displayed")
                # The upload function handles the payment confirmation and rotation restart
                # After Y is pressed, loop continues for next customer
            else:
                print(f"\n✗ FAILED! Could not upload QR to device")
                print(f"QR file saved as: {qr_filename}")
                continue
            
    except KeyboardInterrupt:
        print("\nPayment system stopped")
    except Exception as e:
        print(f"Error: {e}")
    
    # Keep connection alive even when exiting
    print("Payment system closed. Device connection maintained.")

if __name__ == "__main__":
    main()