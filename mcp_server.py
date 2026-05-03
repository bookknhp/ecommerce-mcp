#!/usr/bin/env python3
"""
MCP Server for E-Commerce Operations
Provides tools for AI to manage products, coupons, orders, and generate reports
"""

import json
import subprocess
import sys
from database import Database

db = Database()

# Define available MCP tools
TOOLS = {
    # PRODUCT TOOLS
    "product_update_price": {
        "description": "Update product price",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer", "description": "Product ID"},
                "new_price": {"type": "number", "description": "New price in THB"}
            },
            "required": ["product_id", "new_price"]
        }
    },
    "product_update_stock": {
        "description": "Update product stock quantity",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer", "description": "Product ID"},
                "quantity": {"type": "integer", "description": "New stock quantity"}
            },
            "required": ["product_id", "quantity"]
        }
    },
    "product_delete": {
        "description": "Delete a product (only if no orders)",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "integer", "description": "Product ID to delete"}
            },
            "required": ["product_id"]
        }
    },
    "product_low_stock": {
        "description": "Get all products with low stock",
        "input_schema": {
            "type": "object",
            "properties": {
                "threshold": {"type": "integer", "description": "Stock threshold (default: 5)"}
            }
        }
    },
    
    # COUPON TOOLS
    "coupon_create": {
        "description": "Create a new coupon for promotions",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Coupon code (e.g., SUMMER20)"},
                "name": {"type": "string", "description": "Coupon name"},
                "discount_type": {"type": "string", "enum": ["PERCENTAGE", "FIXED"], "description": "Discount type"},
                "discount_value": {"type": "number", "description": "Discount value"},
                "min_order": {"type": "number", "description": "Minimum order value"},
                "max_uses": {"type": "integer", "description": "Max total uses"},
                "expiry_days": {"type": "integer", "description": "Days until expiry"}
            },
            "required": ["code", "name", "discount_type", "discount_value"]
        }
    },
    "coupon_cleanup_expired": {
        "description": "Mark all expired coupons as expired",
        "input_schema": {"type": "object", "properties": {}}
    },
    "coupon_disable": {
        "description": "Disable a specific coupon",
        "input_schema": {
            "type": "object",
            "properties": {
                "coupon_id": {"type": "integer", "description": "Coupon ID"}
            },
            "required": ["coupon_id"]
        }
    },
    
    # ORDER TOOLS
    "order_update_status": {
        "description": "Update order status",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "Order ID"},
                "status": {"type": "string", "enum": ["pending", "processing", "shipped", "delivered", "cancelled"]}
            },
            "required": ["order_id", "status"]
        }
    },
    "order_update_payment": {
        "description": "Update order payment status",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "integer", "description": "Order ID"},
                "payment_status": {"type": "string", "enum": ["unpaid", "paid", "refunded"]}
            },
            "required": ["order_id", "payment_status"]
        }
    },
    
    # REPORTING TOOLS
    "report_sales": {
        "description": "Generate sales report (optional date range)",
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
            }
        }
    },
    "report_products": {
        "description": "Generate product profitability report",
        "input_schema": {"type": "object", "properties": {}}
    },
    
    # ALERT TOOLS
    "get_alerts": {
        "description": "Get current system alerts (low stock, unpaid orders, etc)",
        "input_schema": {"type": "object", "properties": {}}
    },
    
    # MAINTENANCE TOOLS
    "backup_database": {
        "description": "Create a database backup",
        "input_schema": {"type": "object", "properties": {}}
    },
    "cleanup_old_logs": {
        "description": "Clean up old database logs",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "Delete logs older than N days (default: 30)"}
            }
        }
    }
}


def execute_tool(tool_name, arguments):
    """Execute a specific tool with given arguments"""
    try:
        if tool_name == "product_update_price":
            return db.update_product_price(arguments["product_id"], arguments["new_price"])
        
        elif tool_name == "product_update_stock":
            return db.update_product_stock(arguments["product_id"], arguments["quantity"])
        
        elif tool_name == "product_delete":
            return db.delete_product(arguments["product_id"])
        
        elif tool_name == "product_low_stock":
            threshold = arguments.get("threshold", 5)
            products = db.get_low_stock_products(threshold)
            return {"success": True, "data": products, "count": len(products)}
        
        elif tool_name == "coupon_create":
            return db.create_coupon(
                code=arguments["code"],
                name=arguments["name"],
                discount_type=arguments["discount_type"],
                discount_value=arguments["discount_value"],
                min_order=arguments.get("min_order", 0),
                max_uses=arguments.get("max_uses"),
                expiry_days=arguments.get("expiry_days", 30)
            )
        
        elif tool_name == "coupon_cleanup_expired":
            return db.delete_expired_coupons()
        
        elif tool_name == "coupon_disable":
            return db.disable_coupon(arguments["coupon_id"])
        
        elif tool_name == "order_update_status":
            return db.update_order_status(arguments["order_id"], arguments["status"])
        
        elif tool_name == "order_update_payment":
            return db.update_order_payment_status(arguments["order_id"], arguments["payment_status"])
        
        elif tool_name == "report_sales":
            return db.export_sales_report(
                arguments.get("start_date"),
                arguments.get("end_date")
            )
        
        elif tool_name == "report_products":
            return db.export_product_report()
        
        elif tool_name == "get_alerts":
            return db.get_alerts()
        
        elif tool_name == "backup_database":
            return db.backup_database()
        
        elif tool_name == "cleanup_old_logs":
            days = arguments.get("days", 30)
            return db.cleanup_old_logs(days)
        
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


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
