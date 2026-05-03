import requests
import json
import os
import hmac
import hashlib
import base64
import time

# Configuration (Will be read from Environment Variables in Production)
LIVE_API_URL = os.environ.get("LIVE_API_URL", "https://shop.friday-pet.com/api.php")
JWT_SECRET = os.environ.get("JWT_SECRET_KEY") # IMPORTANT: Set this in Railway!

def base64url_encode(payload):
    if isinstance(payload, dict):
        payload = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    elif isinstance(payload, str):
        payload = payload.encode('utf-8')
    return base64.urlsafe_b64encode(payload).decode('utf-8').replace('=', '')

def generate_admin_token():
    """Generate a valid Admin JWT token using the secret from backup"""
    header = {"alg": "HS256", "typ": "JWT"}
    # Admin User ID is usually 1
    payload = {
        "userId": 1,
        "role": "admin",
        "exp": int(time.time()) + (3600 * 24 * 7) # 7 days
    }
    
    encoded_header = base64url_encode(header)
    encoded_payload = base64url_encode(payload)
    
    signature_base = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        JWT_SECRET.encode('utf-8'),
        signature_base.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    encoded_signature = base64.urlsafe_b64encode(signature).decode('utf-8').replace('=', '')
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def call_live_api(action, params=None, method="GET"):
    """Call the live shop API with admin authentication"""
    token = generate_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json"
    }
    
    url = f"{LIVE_API_URL}?action={action}"
    if params and method == "GET":
        for k, v in params.items():
            url += f"&{k}={v}"
            
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        else:
            response = requests.post(url, headers=headers, json=params, timeout=10)
            
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

# Exported tools that now use LIVE data
def get_live_dashboard():
    return call_live_api("get_admin_dashboard_summary")

def get_live_products():
    return call_live_api("get_products")

def update_live_price(product_id, price):
    return call_live_api("admin_update_product_price", {"id": product_id, "price": price}, "POST")

if __name__ == "__main__":
    # Test connection
    print("Testing Live API Connection...")
    res = get_live_dashboard()
    print(json.dumps(res, indent=2, ensure_ascii=False))
