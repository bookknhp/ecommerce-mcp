# 📱 Telegram Bot - Quick Start Guide

🤖 **E-Commerce Telegram Bot**

ใช้ Telegram สั่งงาน E-commerce จากทุกที่! (แม้จะออกนอก)

---

## ✅ Setup แล้ว

- ✅ **Bot Token:** `8553217591:AAHKOQ0r1Lp4hqfDVkhiFIrioz1Py8V8XSs`
- ✅ **Chat ID:** `5453025761`
- ✅ **Bot Script:** `/Users/bookntp/Desktop/ecommerce-mcp/telegram_bot.py`

---

## 🚀 วิธีรัน

### Terminal 1: รัน Flask Server
```bash
cd /Users/bookntp/Desktop/ecommerce-mcp
python3 app.py
# ✅ http://localhost:5000
```

### Terminal 2: รัน Telegram Bot
```bash
cd /Users/bookntp/Desktop/ecommerce-mcp
python3 telegram_bot.py
```

ตอนนี้ Bot พร้อม! 🎉

---

## 📱 ใช้งานจาก Telegram

### ค้นหา Bot:
```
ใน Telegram ค้นหา username ของ Bot
(หรือกด Start ถ้า Bot เพิ่มคุณมาแล้ว)
```

### Commands ที่มี:

| Command | ตัวอย่าง | ผลลัพธ์ |
|---------|---------|--------|
| `/start` | - | แสดงเมนู |
| `/products` | - | ดูสินค้า & stock ต่ำ |
| `/orders` | - | ดูคำสั่งซื้อ |
| `/coupons` | - | ดูคูปอง |
| `/profit` | - | ดูกำไร |
| `/alerts` | - | ดูเตือน |
| `/customers` | - | ลูกค้า Top 5 |
| `/backup` | - | Backup database |

### Advanced Commands:

```bash
# เปลี่ยนราคาสินค้า ID 47 เป็น 15000
/price 47 15000

# อัพเดท Stock สินค้า 48 เป็น 100
/stock 48 100

# เปลี่ยน Order 5 เป็น shipped
/status 5 shipped

# สร้างคูปอง SUMMER20 ลด 20%
/coupon SUMMER20 "Summer Sale" 20
```

---

## 💬 ตัวอย่างใช้งาน

```
คุณ: /products
Bot: 📦 สินค้า Statistics
     🔢 จำนวนสินค้า: 43
     📊 Stock รวม: 250
     💰 ราคาเฉลี่ย: ฿4,500
     🚨 Stock ต่ำ (12 ชิ้น):
     • iPhone 15: 2 ชิ้น
     • Samsung S24: 1 ชิ้น
     ...

คุณ: /profit
Bot: 💰 Profit Analysis
     💵 ยอดเงินสุทธิ: ฿178,488
     💸 ต้นทุนสินค้า: ฿61,725
     📈 กำไรสุทธิ: ฿77,716
     📊 Profit Margin: 43.54%

คุณ: /price 47 15000
Bot: ✅ Product 47 price updated to ฿15000
```

---

## 🌐 ใช้จากนอก (iPad ที่ข้างนอก)

✅ **ทำงานได้ทั้งหมด!**

```
iPad (ที่ข้างนอก) → Telegram Bot → Server (บ้าน)
                      ↓
                   MCP Server
                      ↓
                   Database
```

ไม่ต้อง setup อะไรพิเศษ - Telegram Bot ใช้ได้ทุกที่ที่มี internet!

---

## 🔒 Security

- ✅ **Only Admin:** Bot ตอบแค่ Chat ID ของคุณเท่านั้น
- ✅ **Token ปลอดภัย:** ลบ token นี้หลังใช้เสร็จ
- ✅ **Read-Write Safe:** ทุก operation มี validation

---

## 🐛 Troubleshooting

| ปัญหา | วิธีแก้ |
|------|--------|
| Bot ไม่ตอบ | ตรวจสอบ Flask Server รันอยู่ |
| Error database | ตรวจสอบ database path ถูกต้อง |
| Token invalid | ใช้ token ที่ถูกต้อง |

---

## 📋 Files

```
ecommerce-mcp/
├── telegram_bot.py      ← Bot script (ใช้ Command Handler)
├── database.py          ← Database operations
├── app.py               ← Flask API (ต้องรัน)
└── TELEGRAM_BOT.md      ← File นี้
```

---

## 🎯 Next Steps

1. ✅ รัน Flask Server (`python3 app.py`)
2. ✅ รัน Telegram Bot (`python3 telegram_bot.py`)
3. ✅ เปิด Telegram และพูดคำสั่ง
4. ✅ Bot ตอบคุณ!

---

**Bot Token:** `8553217591:AAHKOQ0r1Lp4hqfDVkhiFIrioz1Py8V8XSs`  
**Chat ID:** `5453025761`  
**Status:** ✅ Ready!
