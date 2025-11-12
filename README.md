# ESP32 Payment Terminal & POS System

A complete payment terminal and Point of Sale (POS) system for retail businesses, featuring dynamic QR code generation, ESP32 device integration, and web-based POS interface.

## 🚀 Features

### Payment Terminal System
- **Dynamic QR Generation**: Real-time QR codes via ZwennPay API
- **ESP32 Integration**: Direct communication with ESP32 payment terminals
- **Persistent Connections**: Device stays active throughout business hours
- **Image Management**: Upload custom images and control display rotation
- **Robust Error Handling**: Comprehensive error handling and logging

### Web-Based POS System
- **Modern Interface**: Responsive web-based Point of Sale
- **Product Catalog**: Manage inventory with sizes, colors, and stock
- **Shopping Cart**: Add/remove items with quantity controls
- **Real-time Totals**: Automatic calculation with MUR currency
- **Payment Integration**: Seamless QR code generation for customer payments
- **Cloud Deployment**: Run POS in cloud, payment service locally (NEW!)

### Supported Businesses
- ✅ **Coffee Shops** (Artisan Coffee style)
- ✅ **Clothing Stores** (Body & Soul implementation)
- ✅ **Retail Chains** (Easily customizable)

## 📋 Requirements

- Python 3.7+
- ESP32 Payment Terminal (320x480 display)
- Windows OS with COM port access
- ZwennPay API access

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/esp32-payment-terminal.git
cd esp32-payment-terminal
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure device settings:**
Update `config.py` with your COM port (default: COM3, 9600 baud)

## 🎯 Quick Start

### ☁️ Cloud Deployment (Recommended for Production)

For production deployment with cloud-hosted POS and local payment service:

**See:** `CLOUD_DEPLOYMENT_SUMMARY.md` and `DEPLOYMENT_GUIDE.md`

```bash
# Quick demo setup
setup_demo.bat

# Or manual setup - see DEPLOYMENT_GUIDE.md
```

### 💻 Local Development

### 1. Basic Payment Terminal
```bash
python payment_terminal.py
```
Interactive terminal for basic payment operations.

### 2. Dynamic QR Payment System
```bash
python payment_qr.py
```
Enter amounts → Generate QR → Customer pays → Confirm → Next customer

### 3. Web-Based POS (Body & Soul)
```bash
python body_soul_pos.py
```
Open browser: `http://localhost:5000`

## 📱 Applications

### Coffee Shop POS
- Product catalog with beverages and food items
- Quick service workflow
- Real-time QR generation for payments

### Clothing Store POS (Body & Soul)
- Inventory with sizes and colors
- Category filtering (Tops, Bottoms, Accessories)
- Stock management
- Professional retail interface

## 🔧 Tools & Utilities

### Image Management
```bash
python image_uploader.py
```
- Upload custom images (320x480, max 80KB)
- Control display rotation
- Manage device storage

### Batch Image Upload
```bash
python batch_upload.py
```
- Upload multiple images from folder
- Automatic validation and processing

### Port Diagnostics
```bash
python port_diagnostics.py
```
- Detect available COM ports
- Test connection settings
- Troubleshoot device issues

### QR Generator (Standalone)
```bash
python qr_generator.py
```
- Generate QR codes without device upload
- Test ZwennPay API integration

## ⚙️ Configuration

### Device Settings (config.py)
```python
SERIAL_CONFIG = {
    'port': 'COM3',
    'baudrate': 9600,
    'bytesize': 8,
    'parity': 'N',
    'stopbits': 1,
    # ... additional settings
}
```

### ZwennPay Integration
- Merchant ID: 56 (configurable)
- Currency: MUR (Mauritian Rupee)
- Real-time API integration

## 🖼️ Image Specifications

ESP32 Terminal Requirements:
- **Dimensions**: 320x480 pixels (exact)
- **File Size**: Max 80KB
- **Formats**: JPG, JPEG, PNG, BMP
- **File Numbers**: 1-99 (saved as 1.jpeg, 2.jpeg, etc.)

## 🔍 Troubleshooting

### Connection Issues
1. **Run as Administrator** (Windows COM port access)
2. **Check device drivers** in Device Manager
3. **Close other serial applications**
4. **Verify baud rate**: 9600 for most ESP32 devices

### Common Solutions
```bash
# Test port availability
python port_diagnostics.py

# Run with admin privileges
run_as_admin.bat
```

### Device Settings Verification
- Baud rate: 9600
- Data bits: 8
- Parity: None
- Stop bits: 1
- Flow control: None

## 📊 System Architecture

```
Web Browser (POS Interface)
    ↓ HTTP API
Flask Backend (body_soul_pos.py)
    ↓ Function Calls
Payment QR System (payment_qr.py)
    ↓ Serial Communication
ESP32 Payment Terminal (320x480 Display)
    ↓ API Integration
ZwennPay Payment Gateway
```

## 🚀 Production Deployment

### For Coffee Shops
1. Start payment system: `python payment_qr.py`
2. Staff enters amounts throughout the day
3. Device stays active with persistent connection

### For Retail Stores
1. Start web POS: `python body_soul_pos.py`
2. Access via browser on tablet/computer
3. Full product catalog and inventory management

## 📝 Logging

All operations logged to:
- `payment_terminal_YYYYMMDD.log`
- Console output with timestamps
- Error tracking and debugging info

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test with actual ESP32 device
4. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

## 🏪 Business Applications

Successfully implemented for:
- **Artisan Coffee Mauritius** (Coffee shop POS)
- **Body & Soul** (Clothing retail chain)
- **General retail** (Customizable for any business)

## 📞 Support

For technical support or business inquiries:
- Check troubleshooting section
- Run diagnostics tools
- Review log files for detailed error information