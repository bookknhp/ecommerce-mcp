#!/usr/bin/env python3
"""
E-Commerce AI API Server (2026 Stable Edition)
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

app = FastAPI(title="E-Commerce AI API")

# OpenAI Configuration
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
client = None
if OPENAI_KEY:
    try:
        client = OpenAI(api_key=OPENAI_KEY)
        logger.info("OpenAI Client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI Client: {e}")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Error Handler to catch HTML leaks
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"GLOBAL ERROR: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": f"Server error: {str(exc)}"}
    )

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    return FileResponse("dashboard.html")

@app.get("/api/dashboard")
async def get_dashboard():
    try:
        summary = call_live_api("get_admin_dashboard_summary")
        return JSONResponse(content={
            "success": True,
            "data": {
                "sales": summary,
                "orders": {"total_orders": summary.get("total_orders", 0)},
                "profit": summary,
                "low_stock_products": summary.get("low_stock", []),
                "recent_orders": summary.get("recent_orders", []),
                "top_customers": summary.get("top_customers", [])
            }
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/chat")
async def chat_with_ai(request: Request):
    logger.info("Chat request received")
    
    if not client:
        return JSONResponse(status_code=500, content={"success": False, "error": "AI not ready (Missing API Key)"})
    
    try:
        body = await request.json()
        user_message = body.get("message", "")
        
        # Tools & Tools List
        mcp_tools = list_tools()
        openai_tools = [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["inputSchema"]}} for t in mcp_tools]
        
        messages = [
            {"role": "system", "content": "You are a shop manager powered by GPT-5 nano. Always Thai."},
            {"role": "user", "content": user_message}
        ]
        
        # First call
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        
        if msg.tool_calls:
            messages.append(msg)
            for tool in msg.tool_calls:
                res = execute_tool(tool.function.name, json.loads(tool.function.arguments))
                messages.append({"tool_call_id": tool.id, "role": "tool", "name": tool.function.name, "content": json.dumps(res)})
            
            # Second call
            final = client.chat.completions.create(model="gpt-5-nano", messages=messages)
            return JSONResponse(content={"success": True, "reply": final.choices[0].message.content})
        
        return JSONResponse(content={"success": True, "reply": msg.content})

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
