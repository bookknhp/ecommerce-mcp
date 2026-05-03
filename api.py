#!/usr/bin/env python3
"""
E-Commerce AI API Server (2026 Partner Edition)
Direct Implementation from ChatController.php logic
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import json
import logging
import traceback
from openai import OpenAI
from live_bridge import call_live_api
from mcp_server import list_tools, execute_tool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Friday AI Partner API")

# OpenAI Configuration
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
client = None
if OPENAI_KEY:
    client = OpenAI(api_key=OPENAI_KEY)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    return FileResponse("dashboard.html")

@app.get("/api/dashboard")
async def get_dashboard():
    try:
        summary = call_live_api("get_admin_dashboard_summary")
        return JSONResponse(content={"success": True, "data": summary})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/ai-manager")
@app.post("/api/chat")
async def chat_with_ai(request: Request):
    if not client:
        return JSONResponse(status_code=500, content={"success": False, "error": "API Key missing"})
    
    try:
        body = await request.json()
        user_message = body.get("message", "")
        
        # Tools Context
        mcp_tools = list_tools()
        openai_tools = [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["inputSchema"]}} for t in mcp_tools]
        
        # System Prompt (Friday AI Partner Style from ChatController.php)
        system_prompt = (
            "คุณคือ 'Friday AI Partner' เพื่อนคู่คิดที่ฉลาดและเป็นกันเองที่สุดของเจ้าของร้าน\n"
            "คุณเข้าถึงข้อมูลหลังบ้านได้แบบ Real-time และสามารถสั่งงานผ่านเครื่องมือ (Tools) ได้\n\n"
            "กฎเหล็กในการคุย:\n"
            "1. เน้น Insight ไม่เน้นแค่ Data: บอกความหมายของตัวเลขด้วย\n"
            "2. ห้ามใช้ Markdown (** หรือ ###): ให้ใช้ Emoji และการเว้นบรรทัดแทนเพื่อให้สวยงาม\n"
            "3. ตอบเป็นภาษาไทยแบบมืออาชีพแต่เป็นกันเอง\n"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # First call (GPT-5 nano - No temperature as per ChatController.php)
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
            # Temperature omitted for gpt-5 stability
        )
        
        msg = response.choices[0].message
        
        if msg.tool_calls:
            messages.append(msg)
            for tool in msg.tool_calls:
                res = execute_tool(tool.function.name, json.loads(tool.function.arguments))
                messages.append({"tool_call_id": tool.id, "role": "tool", "name": tool.function.name, "content": json.dumps(res, ensure_ascii=False)})
            
            # Second call
            final = client.chat.completions.create(
                model="gpt-5-nano", 
                messages=messages
                # Temperature omitted
            )
            return JSONResponse(content={"success": True, "reply": final.choices[0].message.content})
        
        return JSONResponse(content={"success": True, "reply": msg.content})

    except Exception as e:
        logger.error(f"Chat Error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
