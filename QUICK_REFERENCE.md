# 🎯 E-Commerce MCP - Quick Reference

## 🚀 เริ่มต้น (3 ขั้นตอน)

### Step 1: รัน Flask Server
```bash
cd /Users/bookk/Documents/ecommerce-mcp
python3 app.py
# ✅ http://localhost:5000
```

### Step 2: เข้า Dashboard (Terminal ใหม่)
```bash
cd /Users/bookk/Documents/ecommerce-mcp
python3 -m http.server 8000
# 📊 http://localhost:8000/dashboard.html
```

### Step 3: ตั้ง Claude Desktop (Optional แต่แนะนำ!)
```
1. หา: ~/Library/Application\ Support/Claude/claude_desktop_config.json
2. เพิ่ม:
{
  "mcpServers": {
    "ecommerce": {
      "command": "python3",
      "args": ["/Users/bookk/Documents/ecommerce-mcp/mcp_server.py"]
    }
  }
}
3. รีสตาร์ท Claude Desktop
```

---

## 📊 Dashboard Features

| KPI | คำอธิบาย |
|-----|---------|
| 💰 ยอดรวม | ยอดขายทั้งหมด (บาท) |
| 📦 Order | จำนวนคำสั่งซื้อ |
| 📈 กำไร | กำไรสุทธิ (บาท) |
| 🚨 Stock ต่ำ | สินค้าต้องจัดเก็บ |

---

## 🤖 MCP Tools (สั่งงาน AI)

### 📦 Product
```
"ช่วยดูสินค้า stock ต่ำสุด 5 ชิ้น"
→ product_low_stock(threshold=5)

"เปลี่ยนราคาสินค้า 47 เป็น 15000 บาท"
→ product_update_price(product_id=47, new_price=15000)

"อัพเดท Stock สินค้า 48 เป็น 100 ชิ้น"
→ product_update_stock(product_id=48, quantity=100)
```

### 🏷️ Coupon
```
"สร้างคูปอง SUMMER20 ลด 20% ต่ำสุด 1000 บาท"
→ coupon_create(code="SUMMER20", name="Summer Sale", 
               discount_type="PERCENTAGE", discount_value=20,
               min_order=1000)

"ลบคูปองหมดอายุทั้งหมด"
→ coupon_cleanup_expired()

"ปิดใช้คูปอง 3"
→ coupon_disable(coupon_id=3)
```

### 📋 Order
```
"เปลี่ยน Order 5 เป็น shipped"
→ order_update_status(order_id=5, status="shipped")

"Mark Order 7 เป็น paid"
→ order_update_payment(order_id=7, payment_status="paid")
```

### 📊 Report
```
"สรุปรายงานขายตั้งแต่ 2026-05-01"
→ report_sales(start_date="2026-05-01")

"ดูสินค้าที่มีกำไรสูงสุด"
→ report_products()
```

### 🔔 Alert
```
"แสดงเตือนที่มี"
→ get_alerts()
# ⚠️ Low Stock, Unpaid Orders, Expired Coupons
```

### 🛠️ Maintenance
```
"Backup database"
→ backup_database()

"ล้าง log เก่า 60 วัน"
→ cleanup_old_logs(days=60)
```

---

## 🔌 REST API Examples

### ดึงข้อมูล (GET)
```bash
# Dashboard
curl http://localhost:5000/api/dashboard

# Low Stock
curl http://localhost:5000/api/products/low-stock?threshold=5

# Top Customers
curl http://localhost:5000/api/users/top?limit=10

# Alerts
curl http://localhost:5000/api/alerts
```

### สั่งงาน (POST/PUT/DELETE)
```bash
# เปลี่ยนราคา
curl -X PUT http://localhost:5000/api/products/47/price \
  -d '{"price": 15000}'

# เปลี่ยน Stock
curl -X PUT http://localhost:5000/api/products/47/stock \
  -d '{"quantity": 50}'

# สร้างคูปอง
curl -X POST http://localhost:5000/api/coupons \
  -d '{
    "code": "SAVE50",
    "name": "Save 50 Baht",
    "discount_type": "FIXED",
    "discount_value": 50
  }'

# Update Order Status
curl -X PUT http://localhost:5000/api/orders/5/status \
  -d '{"status": "shipped"}'

# Backup
curl -X POST http://localhost:5000/api/maintenance/backup
```

---

## 🎯 Workflow Examples

### วิธี 1: ใช้ Dashboard ดูข้อมูล
```
1. เปิด http://localhost:8000/dashboard.html
2. ดูสินค้า, Order, ยอดขาย เป็นต้น
3. Auto-refresh ทุก 30 วินาที
```

### วิธี 2: ใช้ MCP ผ่าน Claude
```
1. เปิด Claude Desktop (ถ้าตั้งค่า config แล้ว)
2. พูดอะไรก็ได้:
   "ช่วยดูสินค้า stock ต่ำสุด"
   "สร้างคูปอง WELCOME20 ลด 20%"
   "Update order 5 เป็น shipped"
   "ยอดขายวันนี้เท่าไร"
3. Claude จะใช้ MCP tools ช่วย
```

### วิธี 3: ใช้ REST API ตรง
```bash
# ใน Terminal/Script
curl -X PUT http://localhost:5000/api/products/47/price \
  -d '{"price": 15000}'
```

---

## 🔗 สัญลักษณ์ Status

### Order Status
- `pending` - รอการประมวลผล
- `processing` - กำลังจัดเตรียม
- `shipped` - ส่งแล้ว
- `delivered` - ส่งถึงแล้ว
- `cancelled` - ยกเลิก

### Payment Status
- `unpaid` - ยังไม่ชำระ
- `paid` - ชำระแล้ว
- `refunded` - คืนเงินแล้ว

### Coupon Status
- `ACTIVE` - ใช้ได้
- `INACTIVE` - ปิดใช้งาน
- `EXPIRED` - หมดอายุ

---

## ⚡ Performance Tips

- Dashboard auto-cache 30 วินาที
- MCP tools ผ่าน JSON-RPC เร็ว
- REST API พร้อมทำงาน concurrent
- Database ดึง indexed queries เร็ว

---

## 🐛 Troubleshooting

| ปัญหา | วิธีแก้ |
|------|--------|
| Port 5000 ใช้งาน | `lsof -i :5000` แล้ว `kill -9 <PID>` |
| Dashboard ไม่โหลด | ตรวจสอบ Flask running และ CORS |
| MCP tools ไม่ทำงาน | ตรวจสอบ Claude Desktop config |
| API error 400 | ตรวจสอบ required parameters |
| Database lock | อยู่ draft เท่านั้น ไม่มี concurrent writes |

---

## 📞 Support

- 📖 README.md - เอกสารละเอียด
- 🔧 database.py - โครงสร้าง DB
- 🤖 mcp_server.py - MCP tools
- 💻 app.py - Flask endpoints

---

**Version:** 2.0.0 (MCP Complete)  
**Last Updated:** 2026-05-03  
**Status:** ✅ Ready to Use
