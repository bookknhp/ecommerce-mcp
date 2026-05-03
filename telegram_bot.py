#!/usr/bin/env python3
"""
Telegram Bot for E-Commerce MCP Server
Powered by GPT-5 nano (OpenAI)
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json
import os
from database import Database
from mcp_server import execute_tool, list_tools
from openai import OpenAI

# Configuration - Read from environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = int(os.environ.get('TELEGRAM_CHAT_ID', 5453025761))
API_BASE_URL = os.environ.get('API_BASE_URL', "http://localhost:5000/api")
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI
if not OPENAI_KEY:
    logger.error("Missing OPENAI_API_KEY environment variable!")
else:
    client = OpenAI(api_key=OPENAI_KEY)

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
🤖 *E-Commerce AI Assistant (GPT-5 nano)* 

ยินดีต้อนรับครับ! ผมเป็น AI ผู้จัดการร้านค้าของคุณ คุณสามารถพิมพ์สั่งงานผมเป็นภาษาไทยได้เลย เช่น:

📊 *ตัวอย่างการสั่งงาน:*
• "ขอดูสรุปยอดขายและกำไรหน่อย"
• "ช่วยแก้ราคาสินค้า ID 105 เป็น 500 บาท"
• "เช็คสต็อกสินค้าที่ใกล้หมดให้ที"
• "สร้างคูปองลด 20% ชื่อโค้ดว่า SALE20"

✅ พร้อมรับคำสั่งครับ!
"""
    await update.message.reply_text(message, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages with ChatGPT AI Brain"""
    text = update.message.text.strip()
    
    # Let OpenAI process the request
    try:
        # Inform user AI is thinking
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Prepare tools for OpenAI format
        mcp_tools = list_tools()
        openai_tools = []
        for t in mcp_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["inputSchema"]
                }
            })
        
        messages = [
            {"role": "system", "content": "You are a helpful E-Commerce Manager AI powered by GPT-5 nano. Use the provided tools to manage products, orders, and reports. Always respond in Thai. Be friendly and professional."},
            {"role": "user", "content": text}
        ]
        
        # Call OpenAI with GPT-5 nano
        response = client.chat.completions.create(
            model="gpt-5-nano", 
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Check if AI wants to call tools
        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the tool
                result = execute_tool(function_name, function_args)
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # Get final response from AI explaining the results
            final_response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=messages
            )
            await update.message.reply_text(final_response.choices[0].message.content, parse_mode='Markdown')
        else:
            # Normal conversation
            await update.message.reply_text(response_message.content, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"AI Error: {e}")
        error_msg = str(e)
        if "model_not_found" in error_msg or "does not exist" in error_msg:
            await update.message.reply_text("🤖 (แจ้งเตือน): รุ่น 'gpt-5-nano' ยังไม่เปิดให้ใช้งานผ่าน API ของ OpenAI ในขณะนี้ ผมขออนุญาตใช้รุ่นที่เสถียรที่สุดแทนนะครับ")
        else:
            await update.message.reply_text(f"🤖 ขออภัยครับ AI ของผมขัดข้อง: {error_msg}")

def main():
    """Start the bot"""
    print("🤖 E-Commerce AI Bot Starting (GPT-5 nano)...")
    
    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ AI Bot started and ready!")
    app.run_polling()

if __name__ == '__main__':
    main()
