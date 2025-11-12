# Railway Deployment Guide - Body & Soul POS

Complete guide to deploy your Body & Soul POS system to Railway cloud platform.

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────┐
│   RAILWAY CLOUD                     │
│   body_soul_cloud_enhanced.py       │
│   - Web POS Interface               │
│   - Product Catalog                 │
│   - PostgreSQL Database             │
└──────────────┬──────────────────────┘
               │ HTTP API
               │ (Internet)
               ▼
┌─────────────────────────────────────┐
│   STORE COMPUTER (Local)            │
│   body_soul_local_enhanced.py       │
│   - ESP32 Communication             │
│   - QR Generation                   │
└─────────────────────────────────────┘
```

---

## 📋 Prerequisites

### What You Need:

1. ✅ GitHub account (free)
2. ✅ Railway account (free to start)
3. ✅ Store computer with ESP32 connected
4. ✅ Basic command line knowledge

### Files You Already Have:

- ✅ `body_soul_cloud_enhanced.py` - Cloud service
- ✅ `body_soul_local_enhanced.py` - Local service
- ✅ `requirements_railway.txt` - Cloud dependencies
- ✅ `requirements_local.txt` - Local dependencies
- ✅ `Procfile_railway` - Railway start command
- ✅ `runtime.txt` - Python version
- ✅ `templates/pos_enhanced.html` - Web interface

---

## 🚀 Step 1: Prepare Your Code

### 1.1 Create .gitignore

Create a file named `.gitignore` in your project root:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# Environment
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Temp files
temp_*.jpg
temp_*.png
payment_qr.jpg
```

### 1.2 Rename Procfile

```bash
# Rename Procfile_railway to Procfile
ren Procfile_railway Procfile
```

### 1.3 Update requirements.txt for Railway

```bash
# Copy Railway requirements
copy requirements_railway.txt requirements.txt
```

---

## 🐙 Step 2: Push to GitHub

### 2.1 Initialize Git Repository

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Body & Soul POS Cloud Ready"
```

### 2.2 Create GitHub Repository

1. Go to https://github.com
2. Click "New Repository"
3. Name: `body-soul-pos`
4. Description: "Body & Soul POS System - Cloud Ready"
5. Keep it Private (recommended)
6. Click "Create Repository"

### 2.3 Push Code

```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/body-soul-pos.git

# Push code
git branch -M main
git push -u origin main
```

---

## 🚂 Step 3: Deploy to Railway

### 3.1 Create Railway Account

1. Go to https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access GitHub

### 3.2 Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `body-soul-pos` repository
4. Railway will automatically:
   - Detect Python
   - Read `requirements.txt`
   - Use `Procfile` to start app
   - Deploy!

**Wait 2-3 minutes for deployment...**

### 3.3 Add PostgreSQL Database

1. In your Railway project dashboard
2. Click "New" → "Database" → "Add PostgreSQL"
3. Railway automatically:
   - Creates database
   - Sets `DATABASE_URL` environment variable
   - Connects to your app

**Done! Database is ready.**

---

## ⚙️ Step 4: Configure Environment Variables

### 4.1 Set Environment Variables in Railway

1. Click on your service (body-soul-pos)
2. Go to "Variables" tab
3. Add these variables:

```
LOCAL_SERVICE_URL = http://your-store-ip:8080
LOCAL_API_KEY = your-secret-key-12345-change-this
```

**Note:** We'll update `LOCAL_SERVICE_URL` later with your store computer's IP.

### 4.2 Generate Secure API Key

Use a strong random key:

```bash
# Generate random key (PowerShell)
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

Copy this key and use it for `LOCAL_API_KEY`.

---

## 🌐 Step 5: Get Your Railway URL

### 5.1 Generate Domain

1. In Railway dashboard
2. Click "Settings" tab
3. Scroll to "Domains"
4. Click "Generate Domain"

You'll get something like:
```
https://body-soul-pos-production.up.railway.app
```

### 5.2 Test Your Cloud Service

Open the URL in your browser. You should see:
- ✅ Body & Soul POS interface
- ✅ Products loading
- ✅ Can add items to cart
- ❌ QR generation will fail (expected - local service not running yet)

---

## 💻 Step 6: Setup Local Service (Store Computer)

### 6.1 Install Dependencies

On your store computer:

```bash
# Install local dependencies
pip install -r requirements_local.txt
```

### 6.2 Create .env File

Create `.env` file in your project folder:

```
LOCAL_API_KEY=your-secret-key-12345-change-this
COM_PORT=COM3
```

**Use the SAME API key as Railway!**

### 6.3 Test Local Service

```bash
# Run local service
python body_soul_local_enhanced.py
```

You should see:
```
============================================================
BODY & SOUL LOCAL SERVICE (ENHANCED)
============================================================
Service URL: http://localhost:8080
COM Port: COM3
============================================================
✓ ESP32 device connected successfully
============================================================
```

### 6.4 Test Local Service API

Open another terminal:

```bash
# Test health endpoint
curl http://localhost:8080/health
```

Should return:
```json
{
  "status": "online",
  "device": "connected",
  "com_port": "COM3"
}
```

---

## 🔗 Step 7: Connect Cloud to Local

### 7.1 Option A: Same Network (Testing)

If cloud and local are on same network:

1. Find your store computer's local IP:
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. Update Railway environment variable:
   ```
   LOCAL_SERVICE_URL = http://192.168.1.100:8080
   ```

3. Redeploy Railway (automatic on variable change)

**Limitation:** Only works on same network!

### 7.2 Option B: ngrok (Recommended for Testing)

ngrok creates a public URL for your local service:

1. Download ngrok: https://ngrok.com/download
2. Sign up for free account
3. Install ngrok
4. Run ngrok:
   ```bash
   ngrok http 8080
   ```

5. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

6. Update Railway environment variable:
   ```
   LOCAL_SERVICE_URL = https://abc123.ngrok.io
   ```

**Limitation:** Free ngrok URLs change on restart!

### 7.3 Option C: Static IP (Production)

For production, you need:

1. **Static IP** from your ISP
2. **Port forwarding** on your router:
   - Forward port 8080 to store computer
3. **Firewall rule** to allow port 8080

Then update Railway:
```
LOCAL_SERVICE_URL = http://your-static-ip:8080
```

**This is the production solution!**

---

## ✅ Step 8: Test End-to-End

### 8.1 Start Local Service

On store computer:
```bash
python body_soul_local_enhanced.py
```

### 8.2 Open Cloud POS

Open your Railway URL in browser:
```
https://body-soul-pos-production.up.railway.app
```

### 8.3 Test Complete Flow

1. ✅ Add products to cart
2. ✅ Scan barcode (type: 5901234123457)
3. ✅ Click "Generate Payment QR"
4. ✅ QR appears on ESP32 device
5. ✅ Click "Payment Completed"
6. ✅ Receipt appears
7. ✅ Print receipt

**If all steps work: SUCCESS! 🎉**

---

## 🔍 Troubleshooting

### Cloud Service Issues

**Problem:** "Application failed to respond"
- Check Railway logs (Deployments → View Logs)
- Verify `Procfile` is correct
- Check `requirements.txt` has all dependencies

**Problem:** Database errors
- Verify PostgreSQL is added
- Check `DATABASE_URL` is set automatically
- Check Railway logs for connection errors

### Local Service Issues

**Problem:** "ESP32 device not connected"
- Check USB cable
- Verify COM port (Device Manager)
- Close Arduino IDE or other serial programs
- Run as Administrator

**Problem:** "Cannot connect to local payment device"
- Verify local service is running
- Check `LOCAL_SERVICE_URL` in Railway
- Test with `curl http://localhost:8080/health`
- Check firewall settings

**Problem:** "Unauthorized" error
- Verify `LOCAL_API_KEY` matches in both services
- Check .env file on local computer
- Check Railway environment variables

### Connection Issues

**Problem:** Cloud can't reach local service
- Verify ngrok is running (if using ngrok)
- Check port forwarding (if using static IP)
- Test URL from external network
- Check firewall rules

---

## 📊 Monitoring

### Railway Dashboard

Monitor your cloud service:

1. **Metrics** - CPU, memory, requests
2. **Logs** - Real-time application logs
3. **Deployments** - Deployment history
4. **Usage** - Resource usage and costs

### Local Service Logs

Monitor local service:

```bash
# View logs in real-time
python body_soul_local_enhanced.py
```

Logs show:
- QR generation requests
- ESP32 communication
- Errors and warnings

---

## 💰 Costs

### Railway Pricing

**Hobby Plan ($5/month):**
- 500 hours runtime
- PostgreSQL included
- Perfect for single store

**Pro Plan ($20/month):**
- Unlimited runtime
- Better performance
- Multiple stores

**Free Trial:**
- $5 credit to start
- Test before committing

### Total Monthly Cost

- Railway: $5-20/month
- ngrok (optional): Free or $8/month for static URL
- Internet: Your existing connection

**Total: $5-28/month**

---

## 🔄 Updates and Maintenance

### Update Cloud Service

```bash
# Make changes to code
git add .
git commit -m "Update description"
git push

# Railway auto-deploys!
```

### Update Local Service

```bash
# Stop local service (Ctrl+C)
# Update code
# Restart local service
python body_soul_local_enhanced.py
```

### Database Backups

Railway automatically backs up PostgreSQL:
- Daily backups
- 7-day retention
- One-click restore

---

## 🎓 Best Practices

### Security

✅ Use strong API keys
✅ Keep .env files private
✅ Use HTTPS (Railway provides free)
✅ Regular password changes
✅ Monitor access logs

### Performance

✅ Keep local service running 24/7
✅ Monitor Railway metrics
✅ Optimize database queries
✅ Use connection pooling

### Reliability

✅ Test after each update
✅ Monitor error logs
✅ Have backup plan (local-only mode)
✅ Document your setup

---

## 🆘 Support

### Railway Support

- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Your Setup

- Cloud URL: [Your Railway URL]
- Local Service: [Your store computer]
- Database: PostgreSQL on Railway
- ESP32: COM3

---

## ✅ Deployment Checklist

Before going live:

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] PostgreSQL database added
- [ ] Environment variables set
- [ ] Domain generated
- [ ] Local service running
- [ ] ESP32 connected
- [ ] End-to-end test passed
- [ ] Receipt printing works
- [ ] Barcode scanning works
- [ ] Staff trained
- [ ] Backup plan ready

---

## 🎉 You're Live!

Your Body & Soul POS is now running in the cloud!

**Access from anywhere:**
- Store tablets
- Manager's phone
- Home computer
- Multiple stores

**Professional features:**
- Barcode scanning
- Professional receipts
- VAT compliance
- Real-time inventory
- Transaction history

**Ready for business! 🚀**

---

## 📞 Quick Reference

### URLs

- Cloud POS: `https://your-app.railway.app`
- Local Service: `http://localhost:8080`
- Railway Dashboard: `https://railway.app/dashboard`

### Commands

```bash
# Start local service
python body_soul_local_enhanced.py

# Deploy to Railway
git push

# View Railway logs
# (Use Railway dashboard)

# Test local service
curl http://localhost:8080/health
```

### Environment Variables

**Railway:**
- `LOCAL_SERVICE_URL`
- `LOCAL_API_KEY`
- `DATABASE_URL` (auto-set)

**Local:**
- `LOCAL_API_KEY`
- `COM_PORT`

---

**Congratulations! Your POS system is cloud-ready! 🎊**
