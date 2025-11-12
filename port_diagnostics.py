import serial
import serial.tools.list_ports
import time

def list_all_ports():
    """List all available COM ports with detailed information"""
    print("Available COM Ports:")
    print("=" * 50)
    
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No COM ports found!")
        return []
    
    available_ports = []
    for port in ports:
        print(f"Port: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Hardware ID: {port.hwid}")
        print(f"  Manufacturer: {port.manufacturer}")
        print("-" * 30)
        available_ports.append(port.device)
    
    return available_ports

def test_port_connection(port, baudrates=[9600, 115200, 19200, 38400]):
    """Test connection to a specific port with different baud rates"""
    print(f"\nTesting port {port}:")
    print("=" * 30)
    
    for baudrate in baudrates:
        try:
            print(f"Testing {baudrate} baud... ", end="")
            
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=2,
                write_timeout=2
            )
            
            if ser.is_open:
                print("✓ Connected successfully")
                ser.close()
                return baudrate
            else:
                print("✗ Failed to open")
                
        except serial.SerialException as e:
            if "PermissionError" in str(e) or "Access is denied" in str(e):
                print("✗ Permission denied (port in use or need admin)")
            elif "FileNotFoundError" in str(e):
                print("✗ Port not found")
            else:
                print(f"✗ Error: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
    
    return None

def main():
    print("COM Port Diagnostics Tool")
    print("=" * 50)
    
    # List all available ports
    available_ports = list_all_ports()
    
    if not available_ports:
        return
    
    # Test each port
    for port in available_ports:
        working_baudrate = test_port_connection(port)
        if working_baudrate:
            print(f"\n✓ Port {port} is accessible at {working_baudrate} baud")
        else:
            print(f"\n✗ Port {port} is not accessible")
    
    print("\nRecommendations:")
    print("1. If you see 'Permission denied', try running as administrator")
    print("2. Close any other applications that might be using the port")
    print("3. Check if the device is properly connected and powered on")
    print("4. Use the working baud rate in your config.py file")

if __name__ == "__main__":
    main()