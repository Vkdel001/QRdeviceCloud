# Quick Start Guide - ESP32 Payment Terminal & POS System

## 🚀 How to Run This Project Locally

### Prerequisites
- Python 3.7+ installed
- ESP32 device connected to COM3 (optional for testing)
- Windows OS

---

## Option 1: Basic Python Scripts (Simple)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Individual Applications

**Basic Payment Terminal:**
```bash
python payment_terminal.py
```

**Dynamic QR Payment System:**
```bash
python payment_qr.py
```

**Web POS (Single Application):**
```bash
python body_soul_pos.py
```
Open browser: `http://localhost:5000`

---

## Option 2: Cloud + Local Split (Advanced)

This splits the system into two parts: cloud web interface + local payment service.

### Step 1: Start Local Payment Service

**Using Executable (Recommended):**
```bash
dist\BodySoulLocal.exe
```

**Or Using Python:**
```bash
python body_soul_local.py
```

### Step 2: Start Cloud POS Interface
```bash
python body_soul_cloud.py
```

### Step 3: Access the System
- **POS Interface:** `http://localhost:5000`
- **Local Payment API:** `http://localhost:8080`

---

## Option 3: Utility Tools

**Image Management:**
```bash
python image_uploader.py
```

**Batch Image Upload:**
```bash
python batch_upload.py
```

**Port Diagnostics:**
```bash
python port_diagnostics.py
```

**QR Generator (Standalone):**
```bash
python qr_generator.py
```

---

## 🔧 Troubleshooting

### "Permission Denied" or COM Port Issues
```bash
# Run as Administrator (right-click Command Prompt → Run as Administrator)
```

### Check Available Ports
```bash
python port_diagnostics.py
```

### Test Local Payment Service
```bash
# Check if local service is running
curl http://localhost:8080/health
```

### Multiple Port Options
The local service will automatically try ports: 8080, 8081, 8082, 8083

---

## 🎯 Recommended Workflows

### For Coffee Shops / Simple Payments
```bash
python payment_qr.py
```
- Enter amounts → Generate QR → Customer pays → Next customer

### For Retail Stores / Full POS
```bash
# Terminal 1:
dist\BodySoulLocal.exe

# Terminal 2:
python body_soul_cloud.py
```
- Full product catalog, shopping cart, inventory management
- Access via: `http://localhost:5000`

### For Testing Without ESP32 Device
```bash
python body_soul_cloud.py
```
- Web interface works without hardware
- QR generation will show error (expected without device)

---

## 📱 What Each Option Does

| Command | Purpose | Hardware Required |
|---------|---------|-------------------|
| `payment_terminal.py` | Basic terminal interface | ESP32 device |
| `payment_qr.py` | Simple QR generation | ESP32 device |
| `body_soul_pos.py` | Complete POS system | ESP32 device |
| `body_soul_cloud.py` | Web interface only | None |
| `BodySoulLocal.exe` | Payment service only | ESP32 device |

---

## 🔍 System Status Check

### Verify Everything is Working
1. **Local Service Status:**
   ```bash
   curl http://localhost:8080/health
   ```

2. **Cloud Interface:**
   - Open `http://localhost:5000`
   - Check "Local Status" indicator

3. **ESP32 Device:**
   ```bash
   python port_diagnostics.py
   ```

---

## 💡 Quick Tips

- **Run as Administrator** for COM port access
- **Close other serial applications** (Arduino IDE, etc.)
- **Check Device Manager** for COM port number
- **Default baud rate:** 9600
- **Image specs:** 320x480 pixels, max 80KB

---

## 🆘 Common Issues

**"Local payment device not found"**
- Start `BodySoulLocal.exe` or `python body_soul_local.py`
- Check ESP32 USB connection

**"Permission denied on COM port"**
- Run Command Prompt as Administrator
- Close Arduino IDE or other serial apps

**"Port already in use"**
- The system will automatically try ports 8080-8083
- Check startup logs for actual port number

---

## 🎉 Success!

If everything works:
- ✅ Local service shows "ESP32 device connected successfully"
- ✅ Cloud interface shows "Local Status: Online"
- ✅ You can add products and generate QR codes
- ✅ ESP32 displays the QR code

Ready to process payments! 🚀