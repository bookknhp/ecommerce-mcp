#!/usr/bin/env python3
"""
E-Commerce AI API Server (2026 Edition)
Powered by GPT-5 nano
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json
import logging
from openai import OpenAI
from live_bridge import call_live_api
from mcp_server import list_tools, execute_tool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="E-Commerce AI API", version="2.0.0")

# OpenAI Configuration
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
client = None
if OPENAI_KEY:
    client = OpenAI(api_key=OPENAI_KEY)
else:
    logger.warning("OPENAI_API_KEY not found in environment variables!")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Dashboard
@app.get("/", include_in_schema=False)
async def serve_dashboard():
    return FileResponse("dashboard.html")

# ===== DASHBOARD API (LIVE DATA) =====
@app.get("/api/dashboard")
async def get_dashboard():
    """Get summarized dashboard data from LIVE API"""
    try:
        summary = call_live_api("get_admin_dashboard_summary")
        # Ensure we return valid JSON
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
        logger.error(f"Dashboard Error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/products")
async def get_products():
    res = call_live_api("get_products")
    return JSONResponse(content=res)

@app.get("/api/coupons")
async def get_coupons():
    res = call_live_api("get_publicly_available_coupons")
    return JSONResponse(content=res)

# ===== AI CHAT (GPT-5 NANO) =====
@app.post("/api/chat")
async def chat_with_ai(request: Request):
    if not client:
        return JSONResponse(status_code=500, content={"success": False, "error": "OpenAI API Key not configured"})
    
    try:
        body = await request.json()
        user_message = body.get("message")
        if not user_message:
            return JSONResponse(status_code=400, content={"success": False, "error": "No message provided"})
        
        # Prepare tools
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
            {"role": "system", "content": "You are a helpful E-Commerce Manager AI powered by GPT-5 nano. Use the provided tools to manage the shop. ALWAYS respond in Thai."},
            {"role": "user", "content": user_message}
        ]
        
        # Initial AI call
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Handle Tool Calls
        if response_message.tool_calls:
            messages.append(response_message)
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                logger.info(f"AI calling tool: {function_name}")
                result = execute_tool(function_name, function_args)
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # Final AI call with results
            final_response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=messages
            )
            return JSONResponse(content={"success": True, "reply": final_response.choices[0].message.content})
        else:
            return JSONResponse(content={"success": True, "reply": response_message.content})
            
    except Exception as e:
        logger.error(f"Chat Error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# ===== HEALTH CHECK =====
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "model": "gpt-5-nano", "year": 2026}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
