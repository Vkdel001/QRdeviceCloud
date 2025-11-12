# Local Testing Guide - Before Railway Deployment

Test the split architecture locally before deploying to Railway.

---

## 🎯 Goal

Test both services running on your computer:
- Cloud service on port 5000
- Local service on port 8080
- Both communicating via HTTP

---

## 📋 Prerequisites

```bash
# Install all dependencies
pip install -r requirements.txt
pip install psycopg2-binary
```

---

## 🚀 Quick Start

### Step 1: Create .env File

Create `.env` in project root:

```
LOCAL_SERVICE_URL=http://localhost:8080
LOCAL_API_KEY=test-key-12345
COM_PORT=COM3
```

### Step 2: Start Local Service (Terminal 1)

```bash
python body_soul_local_enhanced.py
```

Expected output:
```
============================================================
BODY & SOUL LOCAL SERVICE (ENHANCED)
============================================================
Service URL: http://localhost:8080
✓ ESP32 device connected successfully
============================================================
```

### Step 3: Start Cloud Service (Terminal 2)

```bash
python body_soul_cloud_enhanced.py
```

Expected output:
```
============================================================
BODY & SOUL POS - CLOUD SERVICE (ENHANCED)
============================================================
POS Interface: http://localhost:5000
Local Service: http://localhost:8080
============================================================
```

### Step 4: Test in Browser

Open: `http://localhost:5000`

Test flow:
1. Add products to cart
2. Scan barcode: 5901234123457
3. Generate Payment QR
4. Check ESP32 displays QR
5. Complete payment
6. View receipt

---

## ✅ Success Indicators

- ✅ Both services start without errors
- ✅ ESP32 connects successfully
- ✅ Products load in browser
- ✅ QR generation works
- ✅ Receipt displays correctly

---

## 🔍 Troubleshooting

**Local service won't start:**
- Check COM port in .env
- Close Arduino IDE
- Run as Administrator

**Cloud can't connect to local:**
- Verify both services running
- Check LOCAL_SERVICE_URL in .env
- Check API key matches

**Database errors:**
- Normal - using SQLite locally
- Will use PostgreSQL on Railway

---

## 📝 Next Steps

Once local testing works:
1. Follow RAILWAY_DEPLOYMENT_GUIDE.md
2. Deploy to Railway
3. Setup production local service

---

**Ready for Railway deployment! 🚀**
