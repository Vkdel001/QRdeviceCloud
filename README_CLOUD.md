# Body & Soul POS - Cloud-Ready Edition

Complete Point of Sale system with cloud deployment support for Railway/Heroku.

---

## 🌟 Features

### Core POS Features
- ✅ **Barcode Scanner Support** - Fast checkout with barcode scanning
- ✅ **Professional Receipts** - Complete with BRN, VAT, sequential numbering
- ✅ **VAT Calculation** - Automatic 15% VAT breakdown (Mauritius compliant)
- ✅ **ESP32 Integration** - Payment terminal with QR code display
- ✅ **Product Catalog** - Manage inventory with sizes, colors, stock
- ✅ **Transaction History** - Complete audit trail

### Cloud Features
- ✅ **Railway Deployment** - One-click cloud deployment
- ✅ **PostgreSQL Support** - Production-ready database
- ✅ **Split Architecture** - Cloud web + Local hardware
- ✅ **Remote Access** - Access POS from anywhere
- ✅ **Multi-Store Ready** - Centralized inventory
- ✅ **Auto-Scaling** - Handles traffic spikes

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   RAILWAY CLOUD                     │
│   - Web POS Interface               │
│   - PostgreSQL Database             │
│   - Business Logic                  │
│   - Product Management              │
└──────────────┬──────────────────────┘
               │
               │ HTTPS API
               │ (Secure)
               │
               ▼
┌─────────────────────────────────────┐
│   STORE COMPUTER (Local)            │
│   - ESP32 Communication             │
│   - QR Code Generation              │
│   - Serial Port Access              │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Option 1: Local Testing

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file
copy .env.example .env

# 3. Start services (automated)
start_local_test.bat

# 4. Open browser
http://localhost:5000
```

### Option 2: Railway Deployment

```bash
# 1. Follow the complete guide
See: RAILWAY_DEPLOYMENT_GUIDE.md

# 2. Quick summary
git init
git add .
git commit -m "Initial commit"
git push

# 3. Deploy on Railway
# - Connect GitHub repo
# - Add PostgreSQL
# - Set environment variables
# - Done!
```

---

## 📁 Project Structure

```
body-soul-pos/
├── body_soul_cloud_enhanced.py    # Cloud service (Railway)
├── body_soul_local_enhanced.py    # Local service (Store)
├── body_soul_pos_enhanced.py      # Original (monolithic)
├── requirements_railway.txt        # Cloud dependencies
├── requirements_local.txt          # Local dependencies
├── Procfile_railway               # Railway start command
├── runtime.txt                    # Python version
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── templates/
│   └── pos_enhanced.html          # Web interface
├── config.py                      # Configuration
├── payment_qr.py                  # QR generation
├── image_uploader.py              # ESP32 uploader
└── docs/
    ├── RAILWAY_DEPLOYMENT_GUIDE.md
    ├── LOCAL_TESTING_GUIDE.md
    └── CLOUD_READY_SUMMARY.md
```

---

## 🔧 Configuration

### Environment Variables

**Cloud Service (.env or Railway):**
```bash
LOCAL_SERVICE_URL=http://your-store-ip:8080
LOCAL_API_KEY=your-secret-key
DATABASE_URL=postgresql://...  # Auto-set by Railway
PORT=5000  # Auto-set by Railway
```

**Local Service (.env):**
```bash
LOCAL_API_KEY=your-secret-key  # Must match cloud
COM_PORT=COM3
PORT=8080
```

---

## 📚 Documentation

### Deployment Guides
- **RAILWAY_DEPLOYMENT_GUIDE.md** - Complete Railway setup (60+ pages)
- **LOCAL_TESTING_GUIDE.md** - Test locally before deploying
- **CLOUD_READY_SUMMARY.md** - Architecture overview

### Feature Guides
- **ENHANCED_POS_GUIDE.md** - Enhanced features guide
- **WHATS_NEW.md** - Feature comparison
- **QUICK_START.md** - Original quick start

---

## 💻 Development

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/body-soul-pos.git
cd body-soul-pos

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
copy .env.example .env
# Edit .env with your settings

# 5. Run local services
python body_soul_local_enhanced.py  # Terminal 1
python body_soul_cloud_enhanced.py  # Terminal 2

# 6. Open browser
http://localhost:5000
```

### Testing

```bash
# Test local service health
curl http://localhost:8080/health

# Test cloud service health
curl http://localhost:5000/health

# Test barcode lookup
curl http://localhost:5000/api/product/barcode/5901234123457
```

---

## 🌐 Deployment

### Railway (Recommended)

**Pros:**
- ✅ Easiest setup
- ✅ Free tier available
- ✅ PostgreSQL included
- ✅ Auto-deploy on git push
- ✅ Modern platform

**Cost:** $5-20/month

See: **RAILWAY_DEPLOYMENT_GUIDE.md**

### Heroku

**Pros:**
- ✅ Well-established
- ✅ Free tier
- ✅ PostgreSQL included

**Cons:**
- ❌ Sleeps after 30 min (free tier)
- ❌ Slower than Railway

**Cost:** $7-25/month

### Render

**Pros:**
- ✅ Good free tier
- ✅ PostgreSQL included
- ✅ Easy setup

**Cost:** $7-25/month

---

## 🔒 Security

### Implemented
- ✅ API key authentication
- ✅ HTTPS encryption (Railway automatic)
- ✅ Environment variable secrets
- ✅ PostgreSQL with encryption
- ✅ Input validation

### Best Practices
- Change default API keys
- Use strong passwords
- Regular security updates
- Monitor access logs
- Backup database regularly

---

## 💰 Pricing

### Cloud Hosting (Railway)
- **Free Trial:** $5 credit
- **Hobby:** $5/month (single store)
- **Pro:** $20/month (multiple stores)

### Optional Services
- **ngrok:** Free or $8/month (static URL)
- **Static IP:** Varies by ISP

### Total Monthly Cost
- **Minimum:** $5/month
- **Recommended:** $13/month
- **Production:** $20/month

**Much cheaper than traditional POS systems!**

---

## 🆘 Troubleshooting

### Common Issues

**"ESP32 device not connected"**
- Check USB cable
- Verify COM port in .env
- Close Arduino IDE
- Run as Administrator

**"Cannot connect to local payment device"**
- Verify local service is running
- Check LOCAL_SERVICE_URL
- Test with curl
- Check firewall settings

**"Database connection error"**
- Verify DATABASE_URL is set
- Check PostgreSQL is running
- Review Railway logs

**"Unauthorized" error**
- Verify API keys match
- Check .env file
- Check Railway environment variables

See: **RAILWAY_DEPLOYMENT_GUIDE.md** for detailed troubleshooting

---

## 📊 Monitoring

### Railway Dashboard
- Real-time metrics (CPU, memory, requests)
- Application logs
- Deployment history
- Resource usage

### Local Service
- Console logs
- ESP32 connection status
- QR generation logs
- Error tracking

---

## 🔄 Updates

### Update Cloud Service
```bash
git add .
git commit -m "Update description"
git push
# Railway auto-deploys!
```

### Update Local Service
```bash
# Stop service (Ctrl+C)
# Update code
python body_soul_local_enhanced.py
```

---

## 🎓 Support

### Documentation
- RAILWAY_DEPLOYMENT_GUIDE.md - Complete deployment guide
- LOCAL_TESTING_GUIDE.md - Local testing
- CLOUD_READY_SUMMARY.md - Architecture overview

### External Resources
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Flask Docs: https://flask.palletsprojects.com

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Railway for cloud platform
- Flask for web framework
- PostgreSQL for database
- ESP32 for payment terminal

---

## 📞 Contact

For support or inquiries:
- Check documentation first
- Review troubleshooting section
- Test locally before deploying

---

## ✅ Checklist

### Before Deployment
- [ ] Tested locally
- [ ] Created GitHub repository
- [ ] Updated .env.example
- [ ] Reviewed security settings
- [ ] Read deployment guide

### After Deployment
- [ ] Verified cloud service works
- [ ] Setup local service
- [ ] Tested end-to-end
- [ ] Trained staff
- [ ] Setup monitoring

---

**Ready to deploy? Follow RAILWAY_DEPLOYMENT_GUIDE.md!**

**Questions? Check the documentation!**

**Good luck! 🚀**
