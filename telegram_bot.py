#!/usr/bin/env python3
"""
Telegram Bot for E-Commerce MCP Server
Access MCP commands via Telegram from anywhere!
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
import os
from database import Database
from mcp_server import execute_tool

# Configuration - Read from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', "8553217591:AAHKOQ0r1Lp4hqfDVkhiFIrioz1Py8V8XSs")
ADMIN_CHAT_ID = int(os.environ.get('TELEGRAM_CHAT_ID', 5453025761))
API_BASE_URL = os.environ.get('API_BASE_URL', "http://localhost:5000/api")

# Initialize database
db = Database()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def format_thai_number(num):
    """Format number in Thai format"""
    if not num:
        return "0"
    return f"{num:,.2f}".replace(",", " ")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    message = """
🤖 *E-Commerce MCP Bot* 

ยินดีต้อนรับ! พิมพ์คำสั่งเพื่อให้ AI ช่วยจัดการ E-commerce

📋 *Commands:*
/products - ดูสินค้า & stock ต่ำ
/orders - ดูคำสั่งซื้อ & สถิติ
/coupons - ดูคูปองที่ใช้ได้
/profit - ดูกำไร & ยอดขาย
/alerts - ดูเตือนระบบ
/customers - ลูกค้า Top 5
/backup - Backup database

🎯 *Advanced Commands:*
/price <id> <price> - เปลี่ยนราคาสินค้า
/stock <id> <qty> - อัพเดท Stock
/coupon <code> <name> <disc> - สร้างคูปอง
/status <order_id> <status> - เปลี่ยน Order Status

✅ พร้อมใช้!
"""
    await update.message.reply_text(message, parse_mode='Markdown')

async def products_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show products with low stock"""
    try:
        low_stock = db.get_low_stock_products(threshold=5)
        stats = db.get_product_stats()
        
        message = f"""
📦 *สินค้า Statistics*

🔢 จำนวนสินค้า: `{stats['total_products']}`
📊 Stock รวม: `{stats['total_stock']}`
💰 ราคาเฉลี่ย: ฿`{format_thai_number(stats['avg_price'])}`
⬆️  สูงสุด: ฿`{format_thai_number(stats['max_price'])}`
⬇️  ต่ำสุด: ฿`{format_thai_number(stats['min_price'])}`

🚨 *Stock ต่ำ ({len(low_stock)} ชิ้น):*
"""
        
        for p in low_stock[:10]:
            message += f"\n• {p['name']}: `{p['stock_quantity']}` ชิ้น"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def orders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show orders statistics"""
    try:
        stats = db.get_order_stats()
        recent = db.get_orders(limit=5)
        
        message = f"""
📋 *Order Statistics*

📦 จำนวนออเดอร์ทั้งหมด: `{stats['total_orders']}`
💰 ยอดรวม: ฿`{format_thai_number(stats['total_revenue'])}`
📊 ราคาเฉลี่ย: ฿`{format_thai_number(stats['avg_order_value'])}`
⏳ รอดำเนินการ: `{stats['pending_orders']}`
❌ ยังไม่ชำระ: `{stats['unpaid_orders']}`

📅 *Order ล่าสุด 5 อัน:*
"""
        
        for o in recent:
            status_emoji = {
                'pending': '⏳',
                'processing': '⚙️',
                'shipped': '📤',
                'delivered': '✅',
                'cancelled': '❌'
            }.get(o['status'], '❓')
            
            message += f"\n• Order #{o['id']}: ฿{format_thai_number(o['total_amount'])} {status_emoji}"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def coupons_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show active coupons"""
    try:
        coupons = db.get_coupons(active_only=True)
        usage = db.get_coupon_usage()
        
        message = f"""
🏷️ *Active Coupons ({len(coupons)})*

"""
        
        for c in coupons[:10]:
            disc_type = "%" if c['discount_type'] == 'PERCENTAGE' else "฿"
            message += f"\n• `{c['code']}` - {c['name']}\n  {c['discount_value']}{disc_type} (หมดอายุ: {c['expiry_date']})"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def profit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show profit analysis"""
    try:
        sales = db.get_sales_analytics()
        profit = db.get_profit_analysis()
        
        message = f"""
💰 *Profit Analysis*

💵 ยอดเงินสุทธิ: ฿`{format_thai_number(profit['net_revenue'])}`
💸 ต้นทุนสินค้า: ฿`{format_thai_number(profit['product_cost'])}`
📮 ค่าขนส่ง: ฿`{format_thai_number(profit['shipping_cost'])}`
⚙️  ค่าจัดการ: ฿`{format_thai_number(profit['operating_cost'])}`
🤝 ค่าคนกลาง: ฿`{format_thai_number(profit['commission'])}`
🧾 ภาษี VAT: ฿`{format_thai_number(profit['vat'])}`

━━━━━━━━━━━━━━━━━━━━
📈 *กำไรสุทธิ: ฿{format_thai_number(profit['net_profit'])}*
📊 Profit Margin: `{profit['profit_margin_percent']:.2f}%`
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def alerts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system alerts"""
    try:
        result = db.get_alerts()
        
        if not result['alerts']:
            message = "✅ ไม่มีเตือน - ทุกอย่างดีสำหรับตอนนี้"
        else:
            message = f"🔔 *System Alerts ({len(result['alerts'])}):*\n\n"
            
            for alert in result['alerts']:
                icon = {
                    'LOW_STOCK': '🚨',
                    'UNPAID_ORDERS': '💳',
                    'EXPIRED_COUPONS': '🏷️'
                }.get(alert['type'], '⚠️')
                
                message += f"{icon} [{alert['severity']}] {alert['message']}\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def customers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top customers"""
    try:
        customers = db.get_top_customers(limit=5)
        
        message = "⭐ *Top 5 Customers:*\n\n"
        
        for i, c in enumerate(customers, 1):
            message += f"{i}. {c['name']}\n"
            message += f"   ยอด: {c['order_count']} order\n"
            message += f"   รวม: ฿{format_thai_number(c['total_spent'] or 0)}\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def backup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Backup database"""
    try:
        result = db.backup_database()
        if result['success']:
            message = f"✅ Backup สำเร็จ!\n\n{result['backup_path']}"
        else:
            message = f"❌ Backup ล้มเหลว: {result.get('error')}"
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages with commands"""
    text = update.message.text.strip()
    
    # /price <id> <price>
    if text.startswith('/price '):
        parts = text.split()
        if len(parts) >= 3:
            try:
                product_id = int(parts[1])
                price = float(parts[2])
                result = db.update_product_price(product_id, price)
                if result['success']:
                    await update.message.reply_text(f"✅ {result['message']}")
                else:
                    await update.message.reply_text(f"❌ {result.get('error')}")
            except Exception as e:
                await update.message.reply_text(f"❌ Format: /price <id> <price>\nError: {str(e)}")
        else:
            await update.message.reply_text("❌ Format: /price <id> <price>")
    
    # /stock <id> <qty>
    elif text.startswith('/stock '):
        parts = text.split()
        if len(parts) >= 3:
            try:
                product_id = int(parts[1])
                qty = int(parts[2])
                result = db.update_product_stock(product_id, qty)
                if result['success']:
                    await update.message.reply_text(f"✅ {result['message']}")
                else:
                    await update.message.reply_text(f"❌ {result.get('error')}")
            except Exception as e:
                await update.message.reply_text(f"❌ Format: /stock <id> <qty>\nError: {str(e)}")
        else:
            await update.message.reply_text("❌ Format: /stock <id> <qty>")
    
    # /status <order_id> <status>
    elif text.startswith('/status '):
        parts = text.split()
        if len(parts) >= 3:
            try:
                order_id = int(parts[1])
                status = parts[2].lower()
                result = db.update_order_status(order_id, status)
                if result['success']:
                    await update.message.reply_text(f"✅ {result['message']}")
                else:
                    await update.message.reply_text(f"❌ {result.get('error')}")
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)}")
        else:
            await update.message.reply_text("❌ Format: /status <order_id> <status>")
    
    # /coupon <code> <name> <disc>
    elif text.startswith('/coupon '):
        parts = text.split(maxsplit=3)
        if len(parts) >= 4:
            try:
                code = parts[1]
                name = parts[2]
                disc_value = float(parts[3])
                result = db.create_coupon(code, name, "PERCENTAGE", disc_value)
                if result['success']:
                    await update.message.reply_text(f"✅ {result['message']}")
                else:
                    await update.message.reply_text(f"❌ {result.get('error')}")
            except Exception as e:
                await update.message.reply_text(f"❌ Format: /coupon <code> <name> <disc%>\nError: {str(e)}")
        else:
            await update.message.reply_text("❌ Format: /coupon <code> <name> <disc%>")
    
    else:
        await update.message.reply_text("❓ ไม่เข้าใจ... พิมพ์ /start เพื่อดูคำสั่ง")

def main():
    """Start the bot"""
    print("🤖 E-Commerce Telegram Bot Starting...")
    print(f"Token: {TELEGRAM_TOKEN[:20]}...")
    print(f"Admin Chat ID: {ADMIN_CHAT_ID}")
    print()
    
    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("products", products_cmd))
    app.add_handler(CommandHandler("orders", orders_cmd))
    app.add_handler(CommandHandler("coupons", coupons_cmd))
    app.add_handler(CommandHandler("profit", profit_cmd))
    app.add_handler(CommandHandler("alerts", alerts_cmd))
    app.add_handler(CommandHandler("customers", customers_cmd))
    app.add_handler(CommandHandler("backup", backup_cmd))
    
    # Add text handler for custom commands
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ Bot started!")
    print("🔗 Listening for messages...")
    print()
    
    # Start polling
    app.run_polling()

if __name__ == '__main__':
    main()
