#!/usr/bin/env python3
"""
MCP Server for E-Commerce Operations
Provides tools for AI to manage products, coupons, orders, and generate reports
"""

import json
import subprocess
import sys
import logging
from live_bridge import call_live_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define available MCP tools
TOOLS = {
    "get_dashboard_stats": {
        "description": "Get overall system dashboard statistics",
        "input_schema": {"type": "object", "properties": {}}
    },
    "list_products": {
        "description": "List all current products",
        "input_schema": {"type": "object", "properties": {}}
    },
    "get_low_stock_products": {
        "description": "Get list of products with low stock",
        "input_schema": {"type": "object", "properties": {}}
    },
    "update_product_price": {
        "description": "Update product price",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer"},
                "price": {"type": "number"}
            },
            "required": ["product_id", "price"]
        }
    },
    "update_product_stock": {
        "description": "Update product stock quantity",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer"},
                "quantity": {"type": "integer"}
            },
            "required": ["product_id", "quantity"]
        }
    },
    "get_sales_analytics": {
        "description": "Get sales analytics report",
        "input_schema": {"type": "object", "properties": {}}
    },
    "get_profit_report": {
        "description": "Generate product profitability report",
        "input_schema": {"type": "object", "properties": {}}
    },
    "create_coupon": {
        "description": "Create a new coupon",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string", "enum": ["PERCENTAGE", "FIXED"]},
                "value": {"type": "number"}
            },
            "required": ["code", "name", "type", "value"]
        }
    },
    "update_order_status": {
        "description": "Update order status",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer"},
                "status": {"type": "string"}
            },
            "required": ["order_id", "status"]
        }
    },
    "create_product": {
        "description": "Create a new product with details",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "number"},
                "description": {"type": "string"},
                "stock": {"type": "integer"},
                "category_id": {"type": "integer"}
            },
            "required": ["name", "price"]
        }
    }
}


def execute_tool(name, args):
    """Execute tool by name with arguments (Now using Live API)"""
    logger.info(f"Executing tool {name} with args {args}")
    
    if name == "get_dashboard_stats":
        return call_live_api("get_admin_dashboard_summary")
    
    elif name == "list_products":
        return call_live_api("get_products")
    
    elif name == "get_low_stock_products":
        return call_live_api("get_products", {"stock_lt": 10})
    
    elif name == "update_product_price":
        return call_live_api("admin_update_product_price", {"id": args.get("product_id"), "price": args.get("price")}, "POST")
    
    elif name == "update_product_stock":
        return call_live_api("admin_update_product_stock", {"id": args.get("product_id"), "quantity": args.get("quantity")}, "POST")
    
    elif name == "get_sales_analytics":
        return call_live_api("get_admin_sales_over_time")
    
    elif name == "get_profit_report":
        return call_live_api("get_admin_product_profit_report")
    
    elif name == "create_coupon":
        return call_live_api("admin_create_coupon", {
            "code": args.get("code"), 
            "name": args.get("name"),
            "type": args.get("type", "PERCENTAGE"),
            "value": args.get("value")
        }, "POST")
    
    elif name == "update_order_status":
        return call_live_api("admin_update_order_status", {"id": args.get("order_id"), "status": args.get("status")}, "POST")
    
    elif name == "create_product":
        return call_live_api("admin_create_product", {
            "name": args.get("name"),
            "price": args.get("price"),
            "description": args.get("description", ""),
            "stock_quantity": args.get("stock", 0),
            "category_id": args.get("category_id", 1)
        }, "POST")
    
    else:
        return {"success": False, "error": f"Tool {name} not implemented for Live API"}


def list_tools():
    """Return list of available tools"""
    tools = []
    for name, config in TOOLS.items():
        tools.append({
            "name": name,
            "description": config["description"],
            "inputSchema": config["input_schema"]
        })
    return tools


def process_request(request_json):
    """Process incoming MCP request"""
    request_type = request_json.get("type")
    
    if request_type == "tools/list":
        return {
            "type": "tools/list",
            "tools": list_tools()
        }
    
    elif request_type == "tools/call":
        tool_name = request_json.get("name")
        arguments = request_json.get("arguments", {})
        result = execute_tool(tool_name, arguments)
        return {
            "type": "tools/result",
            "name": tool_name,
            "result": result
        }
    
    else:
        return {
            "type": "error",
            "error": f"Unknown request type: {request_type}"
        }


if __name__ == "__main__":
    print("MCP Server - E-Commerce Operations", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(f"Available tools: {len(TOOLS)}", file=sys.stderr)
    
    # Read from stdin and process requests
    while True:
        try:
            line = input()
            if not line:
                continue
            
            request = json.loads(line)
            response = process_request(request)
            print(json.dumps(response))
        
        except EOFError:
            break
        except json.JSONDecodeError as e:
            print(json.dumps({
                "type": "error",
                "error": f"Invalid JSON: {str(e)}"
            }))
        except Exception as e:
            print(json.dumps({
                "type": "error",
                "error": str(e)
            }))
