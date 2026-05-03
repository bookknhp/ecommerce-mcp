# 🚀 Railway Setup Guide

## Step 1: สร้าง Railway Account
1. ไปที่ https://railway.app
2. Click "Login" → GitHub (แนะนำ)
3. Authorize Railway

---

## Step 2: Upload ไปยัง GitHub

### ⚠️ ขั้นแรก: เตรียม GitHub Repo

```bash
cd /Users/bookk/Documents/ecommerce-mcp

# สร้าง Git repo
git init
git add .
git commit -m "Initial E-commerce MCP setup"

# สร้าง repo บน GitHub:
# https://github.com/new
# ตั้งชื่อ: ecommerce-mcp
# Copy link: https://github.com/YOUR_USERNAME/ecommerce-mcp.git

git remote add origin https://github.com/YOUR_USERNAME/ecommerce-mcp.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy บน Railway

### Option A: Deploy จาก Railway Dashboard (ง่ายสุด) ⭐

1. ไปที่ https://railway.app/dashboard
2. Click "+ New Project"
3. Click "Deploy from GitHub repo"
4. เลือก repo: `ecommerce-mcp`
5. Railway จะสแกน Procfile โดยอัตโนมัติ
6. ✅ Deploy เสร็จ!

### Option B: Deploy จาก CLI

```bash
# Install Railway CLI
npm install -g @railway/cli
# หรือ (macOS)
brew install railway

# Login
railway login

# เชื่อมต่อกับ GitHub repo
cd /Users/bookk/Documents/ecommerce-mcp
railway connect

# Deploy
railway up
```

---

## Step 4: ตั้งค่า Environment Variables

ใน Railway Dashboard:
1. ไปที่ Project
2. Click "Variables"
3. Add ตัวแปร:

```
TELEGRAM_BOT_TOKEN = 8553217591:AAHKOQ0r1Lp4hqfDVkhiFIrioz1Py8V8XSs
TELEGRAM_CHAT_ID = 5453025761
FLASK_ENV = production
```

---

## Step 5: ตั้งค่า Services (เรียกใช้ 2 processes)

ใน Railway:
1. Click "Services"
2. สร้าง 2 Services จาก Procfile:
   - `web` → Flask API (Port 5000)
   - `bot` → Telegram Bot (24/7 polling)

**Railway จะ Auto-detect จาก Procfile!**

---

## Step 6: ตรวจสอบ URL

ใน Railway Dashboard:
- `web` service → ได้ URL เช่น: https://ecommerce-mcp-production.up.railway.app
- Test: https://ecommerce-mcp-production.up.railway.app/api/dashboard

---

## ⚙️ ปัญหาที่อาจเกิด:

### Port ไม่ตรง
```python
# app.py ต้องอ่าน PORT จากระบบ
import os
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

### Database Path
```python
# ใน database.py ต้องใช้ Relative Path
db_path = os.environ.get('DATABASE_PATH', 'database.db')
conn = sqlite3.connect(db_path)
```

### Telegram Bot ไม่ทำงาน
- ✅ ตรวจสอบ Token ถูก
- ✅ Variables ตั้งค่าถูก
- ✅ Service "bot" กำลังทำงาน

---

## 📊 Dashboard Access

```
http://YOUR_RAILWAY_URL/api/dashboard
```

---

## 🔗 Links

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.app
- GitHub Repo: https://github.com/YOUR_USERNAME/ecommerce-mcp

---

## ✅ Verification

หลังจาก Deploy เสร็จ:

```bash
# Test API
curl https://YOUR_RAILWAY_URL/api/dashboard

# ควรได้ JSON response:
{
  "success": true,
  "data": { ... }
}
```

---

## 🎉 เสร็จ!

ตอนนี้:
- ✅ API ใช้ได้ทั้งที่บ้านและนอก
- ✅ Telegram Bot ทำงาน 24/7
- ✅ Dashboard accessible จากทุกที่
