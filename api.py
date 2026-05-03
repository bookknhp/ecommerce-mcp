#!/usr/bin/env python3
"""FastAPI Server for E-Commerce MCP"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import Database
import os
import json

app = FastAPI(title="E-Commerce MCP API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    return FileResponse("dashboard.html")

# Database
db = Database()

# ===== PRODUCTS =====
@app.get("/api/products")
def get_products(limit: int = 50, search: str = None):
    try:
        products = db.get_products(limit=limit, search=search)
        return {"success": True, "data": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/low-stock")
def get_low_stock(threshold: int = 5):
    try:
        products = db.get_low_stock_products(threshold=threshold)
        return {"success": True, "data": products, "count": len(products)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/stats")
def get_product_stats():
    try:
        stats = db.get_product_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== ORDERS =====
@app.get("/api/orders")
def get_orders(limit: int = 50, status: str = None):
    try:
        orders = db.get_orders(limit=limit, status=status)
        return {"success": True, "data": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/stats")
def get_order_stats():
    try:
        stats = db.get_order_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== COUPONS =====
@app.get("/api/coupons")
def get_coupons(active_only: bool = True):
    try:
        coupons = db.get_coupons(active_only=active_only)
        return {"success": True, "data": coupons}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/coupons/usage")
def get_coupon_usage():
    try:
        usage = db.get_coupon_usage()
        return {"success": True, "data": usage}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== SALES =====
@app.get("/api/sales/analytics")
def get_sales_analytics():
    try:
        analytics = db.get_sales_analytics()
        return {"success": True, "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sales/profit")
def get_profit_analysis():
    try:
        profit = db.get_profit_analysis()
        return {"success": True, "data": profit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== USERS =====
@app.get("/api/users")
def get_users(limit: int = 50):
    try:
        users = db.get_users(limit=limit)
        return {"success": True, "data": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/top")
def get_top_customers():
    try:
        customers = db.get_top_customers()
        return {"success": True, "data": customers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== DASHBOARD =====
@app.get("/api/dashboard")
def get_dashboard():
    try:
        dashboard = {
            "products": db.get_product_stats(),
            "orders": db.get_order_stats(),
            "sales": db.get_sales_analytics(),
            "profit": db.get_profit_analysis(),
            "low_stock": db.get_low_stock_products(threshold=5),
            "top_customers": db.get_top_customers(),
            "recent_orders": db.get_orders(limit=10),
            "coupons": db.get_coupons(active_only=True),
        }
        return {"success": True, "data": dashboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== WRITE OPERATIONS =====
@app.put("/api/products/{product_id}/price")
def update_product_price(product_id: int, price: float):
    try:
        result = db.update_product_price(product_id, price)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/products/{product_id}/stock")
def update_product_stock(product_id: int, quantity: int):
    try:
        result = db.update_product_stock(product_id, quantity)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/orders/{order_id}/status")
def update_order_status(order_id: int, status: str):
    try:
        result = db.update_order_status(order_id, status)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coupons")
def create_coupon(code: str, name: str, discount_type: str, discount_value: float, 
                  min_order: int = 0, max_uses: int = None, expiry_days: int = 30):
    try:
        result = db.create_coupon(
            code=code,
            name=name,
            discount_type=discount_type,
            discount_value=discount_value,
            min_order=min_order,
            max_uses=max_uses,
            expiry_days=expiry_days
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coupons/cleanup")
def delete_expired_coupons():
    try:
        result = db.delete_expired_coupons()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/coupons/{coupon_id}/disable")
def disable_coupon(coupon_id: int):
    try:
        result = db.disable_coupon(coupon_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== HEALTH CHECK =====
@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "E-Commerce MCP API",
        "version": "1.0.0",
        "database": "connected"
    }

# ===== ROOT =====
@app.get("/api")
def api_root():
    return {
        "service": "E-Commerce MCP API",
        "version": "1.0.0",
        "endpoints": {
            "Products": {
                "list": "/api/products",
                "low_stock": "/api/products/low-stock",
                "stats": "/api/products/stats"
            },
            "Orders": {
                "list": "/api/orders",
                "stats": "/api/orders/stats"
            },
            "Coupons": {
                "list": "/api/coupons",
                "usage": "/api/coupons/usage"
            },
            "Sales": {
                "analytics": "/api/sales/analytics",
                "profit": "/api/sales/profit"
            },
            "Users": {
                "list": "/api/users",
                "top_customers": "/api/users/top"
            },
            "Dashboard": "/api/dashboard"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run(app, host="0.0.0.0", port=port)
