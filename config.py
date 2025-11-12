# Payment Terminal Configuration

# Serial Connection Settings
SERIAL_CONFIG = {
    'port': 'COM3',
    'baudrate': 9600,  # Updated to match device settings
    'bytesize': 8,     # Data bits
    'parity': 'N',     # None
    'stopbits': 1,     # Stop bits
    'timeout': 5,
    'write_timeout': 5,
    'xonxoff': False,  # Software flow control
    'rtscts': False,   # Hardware flow control
    'dsrdtr': False    # Hardware flow control
}

# Message Templates - Customize these for your terminal
MESSAGE_TEMPLATES = {
    'welcome': "WelcomeScreen**bonrix",
    'final': "DisplayTotalScreen**2390.32**50**50**2390.32",
    'to_pay': "DisplayQRCodeScreen**upi://pay?pa=63270083167.payswiff@indus&pn=Bonrix&cu=INR&am=200&pn=Bonrix%20Software%20Systems**200**7418529631@icici",
    'success': "DisplaySuccessQRCodeScreen**1234567890**ORD10594565**29-03-2023",
    'fail': "DisplayFailQRCodeScreen**1234567890**ORD10594565**29-03-2023",
    'cancel': "DisplayCancelQRCodeScreen**1234567890**ORD10594565**29-03-2023"
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'log_to_file': True,
    'log_to_console': True
}

# Connection Settings
CONNECTION_CONFIG = {
    'connection_retry_attempts': 3,
    'connection_retry_delay': 2,  # seconds
    'stabilization_delay': 2  # seconds to wait after connection
}