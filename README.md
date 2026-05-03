# 🚀 E-Commerce MCP Dashboard & Server

**AI-Powered Analytics Dashboard + MCP Server** สำหรับ E-commerce ของคุณ

ช่วยให้ AI สามารถ:
- 📊 **ดูข้อมูล** - สินค้า, คำสั่งซื้อ, คูปอง
- 🎮 **สั่งงาน** - เปลี่ยนราคา, อัพเดท stock, สร้างคูปอง
- 📈 **วิเคราะห์** - ยอดขาย, กำไร, รายงาน
- 🔔 **แจ้งเตือน** - Stock ต่ำ, Order รออยู่

---

## ✅ ตรวจสอบการติดตั้ง

✅ **Flask Server** ทำงานที่ `http://localhost:5000`
✅ **MCP Server** พร้อมใช้ (โครงสร้าง JSON-RPC)
✅ **Database** เชื่อมต่อ: `/Users/bookk/Documents/FULL_BACKUP_20260503_0050/data/shop_main.sqlite`
✅ **API Endpoints** 20+ endpoints พร้อมใช้งาน

---

## 🌐 วิธีใช้งาน

### **บนคอมพิวเตอร์:**

#### 1. รัน Flask Server (Dashboard + REST API):
```bash
cd /Users/bookk/Documents/ecommerce-mcp
python3 app.py
# เปิด http://localhost:5000
```

#### 2. เข้า Dashboard:
```bash
# Option A: ผ่าน Browser โดยตรง
http://localhost:8000/dashboard.html

# Option B: เปิด HTTP Server (ใหม่)
python3 -m http.server 8000
# แล้วเปิด http://localhost:8000/dashboard.html
```

### **บนมือถือ (เดือก Network เดียว):**
```
1. ดูว่า IP ของคอม: 192.168.X.X
2. เปิด Browser มือถือ: http://192.168.X.X:8000/dashboard.html
```

---

## 🤖 ใช้งานกับ AI (MCP Server)

### **วิธี 1: Claude Desktop (ทำเลย!)**

1. หา config file ของ Claude Desktop:
   ```
   Mac: ~/Library/Application\ Support/Claude/claude_desktop_config.json
   Windows: %APPDATA%\Claude\claude_desktop_config.json
   ```

2. เปิด file และเพิ่มส่วนนี้:
   ```json
   {
     "mcpServers": {
       "ecommerce": {
         "command": "python3",
         "args": ["/Users/bookk/Documents/ecommerce-mcp/mcp_server.py"]
       }
     }
   }
   ```

3. รีสตาร์ท Claude Desktop

4. ตอนนี้สามารถใช้ MCP Tools ได้แล้ว!

### **ตัวอย่างการใช้งาน:**

```
ผม (AI): "ช่วยดูสินค้าที่ stock ต่ำสุด 5 ชิ้น"
         ↓
Claude → เรียก tool: product_low_stock(threshold=5)
         ↓
MCP Server → Query database
         ↓
ผม: "พบ 3 สินค้า..."
```

---

## 📊 ฟีเจอร์ Dashboard

### **KPI Cards:**
- 💰 **ยอดรวม** - ยอดขายทั้งหมด
- 📦 **คำสั่งซื้อ** - จำนวนรวม
- 📈 **กำไรสุทธิ** - ผลประกอบการ
- 🚨 **Stock ต่ำ** - สินค้าต้องจัดเก็บ

### **รายละเอียด:**
- 🚨 สินค้า Stock ต่ำ
- 📋 คำสั่งซื้อล่าสุด
- ⭐ ลูกค้า Top 5
- 🏷️ คูปองใช้ได้

---

## 🔌 API Endpoints

### **Read Operations (GET)**

| Endpoint | คำอธิบาย |
|----------|---------|
| `GET /api/dashboard` | Dashboard สรุปทั้งหมด |
| `GET /api/products` | ดึงสินค้า |
| `GET /api/products/low-stock` | สินค้า stock ต่ำ |
| `GET /api/products/stats` | สถิติสินค้า |
| `GET /api/orders` | ดึงคำสั่งซื้อ |
| `GET /api/orders/stats` | สถิติคำสั่งซื้อ |
| `GET /api/coupons` | ดึงคูปอง |
| `GET /api/coupons/usage` | ผลใช้คูปอง |
| `GET /api/sales/analytics` | วิเคราะห์ยอดขาย |
| `GET /api/sales/profit` | คำนวณกำไร |
| `GET /api/users` | ดึงผู้ใช้ |
| `GET /api/users/top` | ลูกค้า Top N |
| `GET /api/alerts` | ดึงเตือน |
| `GET /api/reports/sales` | รายงานขาย |
| `GET /api/reports/products` | รายงานสินค้า |

### **Write Operations (POST/PUT/DELETE)**

| Method | Endpoint | คำอธิบาย |
|--------|----------|---------|
| `PUT` | `/api/products/<id>/price` | เปลี่ยนราคา |
| `PUT` | `/api/products/<id>/stock` | อัพเดท Stock |
| `DELETE` | `/api/products/<id>` | ลบสินค้า |
| `POST` | `/api/coupons` | สร้างคูปอง |
| `POST` | `/api/coupons/cleanup` | ลบคูปองหมดอายุ |
| `PUT` | `/api/coupons/<id>/disable` | ปิดใช้คูปอง |
| `PUT` | `/api/orders/<id>/status` | เปลี่ยนสถานะ Order |
| `PUT` | `/api/orders/<id>/payment-status` | เปลี่ยนสถานะชำระเงิน |
| `POST` | `/api/maintenance/backup` | Backup Database |
| `POST` | `/api/maintenance/cleanup` | ล้าง Log เก่า |

---

## 🎮 MCP Tools

### **Product Tools:**
- `product_update_price` - เปลี่ยนราคาสินค้า
- `product_update_stock` - อัพเดท Stock
- `product_delete` - ลบสินค้า
- `product_low_stock` - ดูสินค้า Stock ต่ำ

### **Coupon Tools:**
- `coupon_create` - สร้างคูปองใหม่
- `coupon_cleanup_expired` - ลบคูปองหมดอายุ
- `coupon_disable` - ปิดใช้คูปอง

### **Order Tools:**
- `order_update_status` - เปลี่ยนสถานะ (pending/processing/shipped/delivered/cancelled)
- `order_update_payment` - เปลี่ยนสถานะชำระเงิน (unpaid/paid/refunded)

### **Reporting Tools:**
- `report_sales` - สรุปยอดขาย (รองรับวันที่)
- `report_products` - รายงานกำไรสินค้า

### **Alert Tools:**
- `get_alerts` - ดึงเตือนระบบ (Low Stock, Unpaid Orders, Expired Coupons)

### **Maintenance Tools:**
- `backup_database` - Backup Database
- `cleanup_old_logs` - ล้าง Log เก่า

---

## 🛠️ ตัวอย่าง API Usage

### ดึงสินค้า Stock ต่ำ:
```bash
curl http://localhost:5000/api/products/low-stock?threshold=5
```

### เปลี่ยนราคาสินค้า:
```bash
curl -X PUT http://localhost:5000/api/products/1/price \
  -H "Content-Type: application/json" \
  -d '{"price": 2500}'
```

### สร้างคูปองใหม่:
```bash
curl -X POST http://localhost:5000/api/coupons \
  -H "Content-Type: application/json" \
  -d '{
    "code": "SUMMER20",
    "name": "Summer Sale",
    "discount_type": "PERCENTAGE",
    "discount_value": 20,
    "min_order": 1000,
    "expiry_days": 30
  }'
```

### อัพเดท Order Status:
```bash
curl -X PUT http://localhost:5000/api/orders/5/status \
  -H "Content-Type: application/json" \
  -d '{"status": "shipped"}'
```

### ดึงยอดขาย:
```bash
curl http://localhost:5000/api/sales/analytics
```

### ดึง Alert ระบบ:
```bash
curl http://localhost:5000/api/alerts
```

---

## 🔄 Auto-Refresh

Dashboard จะ auto-refresh ทุก 30 วินาที เพื่อดึงข้อมูลล่าสุด

---

## 📂 Project Structure

```
ecommerce-mcp/
├── app.py                          ← Flask API Server
├── mcp_server.py                   ← MCP Server (สำหรับ Claude/AI)
├── database.py                     ← Database Connection & Queries
├── dashboard.html                  ← Dashboard UI
├── claude_desktop_config.json      ← Config สำหรับ Claude Desktop
├── requirements.txt                ← Dependencies
└── README.md                       ← นี่คือไฟล์นี้
```

---

## 🚀 การรัน (อย่างละเอียด)

### **Step 1: รัน Flask Server**
```bash
cd /Users/bookk/Documents/ecommerce-mcp
python3 app.py

# Output:
# * Running on http://127.0.0.1:5000
# * Running on http://192.168.0.20:5000
```

### **Step 2: เข้า Dashboard (ในเทอร์มินอล/TTY ใหม่)**
```bash
cd /Users/bookk/Documents/ecommerce-mcp
python3 -m http.server 8000

# แล้วเปิด: http://localhost:8000/dashboard.html
```

### **Step 3: ตั้งค่า Claude Desktop (Optional)**
- ทำตามขั้นตอน "วิธี 1: Claude Desktop" ด้านบน
- รีสตาร์ท Claude Desktop
- ตอนนี้สามารถใช้ MCP Tools ได้!

---

## ⚠️ ข้อควรรู้

- 🔒 **ไม่มี Authentication** - สำหรับ Dev/Testing เท่านั้น
- 📡 **CORS เปิด** - สามารถเข้าจาก Domain ใดๆ
- 🗄️ **SQLite ใช้ Read-Only (Dashboard)** - ไม่ Edit ข้อมูล (ปลอดภัย)
- ✏️ **Write Operations** - ผ่าน API/MCP Toolsเท่านั้น
- 📝 **Auto Backup** - เมื่อใช้ tool `backup_database`

---

## 🔧 Troubleshooting

### **Port 5000 ถูกใช้งาน:**
```bash
# หาว่าใครใช้
lsof -i :5000

# ปิด process
kill -9 <PID>
```

### **Dashboard ไม่โหลด:**
- ตรวจสอบ Flask Server กำลังรัน
- ตรวจสอบ CORS ไม่ block
- ดู Browser Console สำหรับ errors

### **MCP Tools ไม่ทำงาน:**
- ตรวจสอบ config file ของ Claude Desktop
- ตรวจสอบ path สมบูรณ์
- รีสตาร์ท Claude Desktop

---

## 📝 Notes

- Database อัพเดทแบบ Real-time
- Dashboard cache บน Browser แต่ refresh ทุก 30 วินาที
- มี Error handling สำหรับเมื่อ API ไม่ตอบสนอง
- MCP Server เปิด JSON-RPC protocol สำหรับ AI tools

---

## 💡 ไอเดียสำหรับอนาคต

- 🔐 Add Authentication (JWT/API Keys)
- 📨 Email Notifications
- 📞 Telegram Bot Integration
- 📊 Advanced Analytics & Charts
- 🔄 Real-time Sync ด้วย WebSocket
- 🗄️ Multi-database Support

---

**สร้างโดย:** Copilot (GitHub)  
**เวอร์ชัน:** 2.0.0 (MCP Upgrade)  
**สุดท้ายอัพเดท:** 2026-05-03  
**Status:** ✅ Ready for Production (Dev Mode)

