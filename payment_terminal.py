import serial
import serial.tools.list_ports
import logging
import time
from datetime import datetime
from typing import Dict, Optional, List
import requests
import qrcode
from PIL import Image
from config import SERIAL_CONFIG

class PaymentTerminalController:
    """Controller for payment terminal serial communication"""
    
    def __init__(self, com_port: str = None, serial_config: dict = None):
        self.serial_config = serial_config or SERIAL_CONFIG
        self.com_port = com_port or self.serial_config['port']
        self.ser: Optional[serial.Serial] = None
        self.setup_logging()
        
        # Command mappings
        self.commands = {
            '1': "welcome",
            '2': "final", 
            '3': "to_pay",
            '4': "success",
            '5': "fail",
            '6': "cancel",
            '0': "exit"
        }
        
        # Message templates
        self.messages = {
            'welcome': "WelcomeScreen**bonrix",
            'final': "DisplayTotalScreen**2390.32**50**50**2390.32",
            'to_pay': "DisplayQRCodeScreen**upi://pay?pa=63270083167.payswiff@indus&pn=Bonrix&cu=INR&am=200&pn=Bonrix%20Software%20Systems**200**7418529631@icici",
            'success': "DisplaySuccessQRCodeScreen**1234567890**ORD10594565**29-03-2023",
            'fail': "DisplayFailQRCodeScreen**1234567890**ORD10594565**29-03-2023",
            'cancel': "DisplayCancelQRCodeScreen**1234567890**ORD10594565**29-03-2023"
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'payment_terminal_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def generate_dynamic_qr(self) -> bool:
        """Generate QR from ZwennPay API and upload to ESP32"""
        try:
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
            
            self.logger.info("Calling ZwennPay API for dynamic QR...")
            response = requests.post(
                "https://api.zwennpay.com:9425/api/v1.0/Common/GetMerchantQR",
                headers={"accept": "text/plain", "Content-Type": "application/json"},
                json=payload,
                timeout=20
            )
            
            response.raise_for_status()
            upi_data = response.text.strip()
            self.logger.info(f"Got UPI data: {len(upi_data)} characters")
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(upi_data)
            qr.make(fit=True)
            
            # Create QR image and resize to 320x480 canvas
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Create 320x480 canvas and center the QR code
            canvas = Image.new('RGB', (320, 480), 'white')
            qr_size = 280  # QR size that fits nicely in 320x480
            qr_resized = qr_image.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            # Center the QR on the canvas
            x_offset = (320 - qr_size) // 2
            y_offset = (480 - qr_size) // 2
            canvas.paste(qr_resized, (x_offset, y_offset))
            
            # Save temporary QR image
            temp_qr_path = "temp_payment_qr.png"
            canvas.save(temp_qr_path)
            self.logger.info("QR code generated and resized")
            
            # Upload to ESP32 as slot 1 (more likely to be in rotation)
            if self.upload_qr_image(temp_qr_path, 1):
                self.logger.info("Dynamic QR uploaded successfully")
                return True
            else:
                self.logger.error("Failed to upload QR to ESP32")
                return False
                
        except Exception as e:
            self.logger.error(f"Error generating dynamic QR: {e}")
            return False
    
    def upload_qr_image(self, image_path: str, file_number: int) -> bool:
        """Upload QR image to ESP32 using proven working method"""
        try:
            from image_uploader import ESP32ImageUploader
            
            # Create temporary uploader with existing connection
            temp_uploader = ESP32ImageUploader()
            temp_uploader.ser = self.ser  # Use existing connection
            temp_uploader.logger = self.logger
            
            # Use the proven upload method
            return temp_uploader.upload_image(image_path, file_number, chunk_size=1024)
            
        except Exception as e:
            self.logger.error(f"Error uploading QR image: {e}")
            return False
    
    def list_available_ports(self) -> List[str]:
        """List all available COM ports"""
        ports = serial.tools.list_ports.comports()
        available_ports = []
        for port in ports:
            available_ports.append(f"{port.device} - {port.description}")
        return available_ports
    
    def connect(self) -> bool:
        """Establish serial connection to payment terminal"""
        try:
            config = self.serial_config
            self.logger.info(f"Attempting to connect to {self.com_port} with settings:")
            self.logger.info(f"  Baud rate: {config['baudrate']}")
            self.logger.info(f"  Data bits: {config['bytesize']}")
            self.logger.info(f"  Parity: {config['parity']}")
            self.logger.info(f"  Stop bits: {config['stopbits']}")
            
            self.ser = serial.Serial(
                port=self.com_port,
                baudrate=config['baudrate'],
                bytesize=config['bytesize'],
                parity=config['parity'],
                stopbits=config['stopbits'],
                timeout=config['timeout'],
                write_timeout=config['write_timeout'],
                xonxoff=config['xonxoff'],
                rtscts=config['rtscts'],
                dsrdtr=config['dsrdtr']
            )
            
            # Wait for connection to stabilize
            time.sleep(2)
            
            if self.ser.is_open:
                self.logger.info(f"Successfully connected to {self.com_port}")
                return True
            else:
                self.logger.error("Failed to open serial connection")
                return False
                
        except serial.SerialException as e:
            self.logger.error(f"Serial connection error: {e}")
            if "PermissionError" in str(e) or "Access is denied" in str(e):
                self.logger.error("Permission denied - try running as administrator or close other applications using the port")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
                self.logger.info("Serial connection closed")
            except Exception as e:
                self.logger.error(f"Error closing serial connection: {e}")
    
    def send_command(self, command: str) -> Optional[str]:
        """Send command to payment terminal and read response"""
        if not self.ser or not self.ser.is_open:
            self.logger.error("Serial connection not available")
            return None
        
        try:
            # Prepare command with newline
            command_with_newline = command + '\n'
            
            self.logger.info(f"Sending command: {command}")
            
            # Send command
            bytes_written = self.ser.write(command_with_newline.encode('utf-8'))
            self.logger.debug(f"Bytes written: {bytes_written}")
            
            # Flush output buffer
            self.ser.flush()
            
            # Read response
            response = self.ser.readline().decode('utf-8').strip()
            
            if response:
                self.logger.info(f"Received response: {response}")
                return response
            else:
                self.logger.warning("No response received from terminal")
                return None
                
        except serial.SerialTimeoutException:
            self.logger.error("Timeout while communicating with terminal")
            return None
        except serial.SerialException as e:
            self.logger.error(f"Serial communication error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during command send: {e}")
            return None
    
    def display_menu(self):
        """Display available commands to user"""
        print("\n" + "="*50)
        print("PAYMENT TERMINAL CONTROLLER")
        print("="*50)
        print("Press '1' for Welcome Message")
        print("Press '2' for Final Invoice Message")
        print("Press '3' for To Pay QR")
        print("Press '4' for Payment Success Message")
        print("Press '5' for Payment Fail Message")
        print("Press '6' for Payment Cancel Message")
        print("Press '0' to Exit")
        print("="*50)
    
    def get_user_input(self) -> str:
        """Get and validate user input"""
        while True:
            try:
                choice = input("\nEnter command number (0-6): ").strip()
                
                if choice in self.commands:
                    return choice
                else:
                    print("Invalid choice. Please enter a number between 0 and 6.")
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                return '0'
            except Exception as e:
                self.logger.error(f"Error getting user input: {e}")
                print("Error reading input. Please try again.")
    
    def run(self):
        """Main program loop"""
        self.logger.info("Starting Payment Terminal Controller")
        
        # Show available ports
        available_ports = self.list_available_ports()
        if available_ports:
            self.logger.info("Available COM ports:")
            for port in available_ports:
                self.logger.info(f"  {port}")
        
        # Establish connection
        if not self.connect():
            print("\nFailed to connect to payment terminal. Please check:")
            print(f"1. Device is connected to {self.com_port}")
            print("2. Device is powered on")
            print("3. No other applications are using the port")
            print("4. Try running as administrator")
            print("5. Check if baud rate matches device settings")
            print("\nAvailable COM ports:")
            for port in available_ports:
                print(f"   {port}")
            return
        
        try:
            self.display_menu()
            
            while True:
                choice = self.get_user_input()
                
                command_key = self.commands[choice]
                
                if command_key == 'exit':
                    self.logger.info("User requested exit")
                    break
                
                # Handle dynamic QR for payment option
                if command_key == 'to_pay':
                    print(f"\nGenerating dynamic QR for payment...")
                    if self.generate_dynamic_qr():
                        # Stop rotation first, then restart to include new QR
                        print("Stopping current rotation...")
                        stop_response = self.send_command("stoprotation")
                        time.sleep(1)  # Brief pause
                        
                        print("Starting rotation with new QR...")
                        start_response = self.send_command("startrotation")
                        print("✓ Dynamic QR uploaded - rotation restarted")
                        if start_response:
                            print(f"Terminal Response: {start_response}")
                        else:
                            print("Rotation restarted (QR should appear in rotation)")
                    else:
                        print("✗ Failed to generate dynamic QR, using fallback")
                        # Fallback to original static message
                        message = self.messages[command_key]
                        response = self.send_command(message)
                        if response:
                            print(f"Terminal Response: {response}")
                else:
                    # Get message for other commands
                    if command_key in self.messages:
                        message = self.messages[command_key]
                        
                        print(f"\nSending: {command_key.upper()}")
                        response = self.send_command(message)
                        
                        if response:
                            print(f"Terminal Response: {response}")
                        else:
                            print("No response received or communication error")
                    else:
                        self.logger.error(f"Unknown command key: {command_key}")
                        print("Internal error: Unknown command")
        
        except KeyboardInterrupt:
            self.logger.info("Program interrupted by user")
            print("\nProgram interrupted")
        
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            print(f"Unexpected error: {e}")
        
        finally:
            self.disconnect()
            self.logger.info("Payment Terminal Controller stopped")


def main():
    """Main entry point"""
    controller = PaymentTerminalController()
    controller.run()


if __name__ == "__main__":
    main()