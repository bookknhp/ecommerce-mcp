from flask import Flask, jsonify, request
from flask_cors import CORS
from database import Database
import json
import os

app = Flask(__name__)
CORS(app)
db = Database()

# ===== PRODUCTS API =====
@app.route('/api/products', methods=['GET'])
def get_products():
    limit = request.args.get('limit', 50, type=int)
    search = request.args.get('search', None)
    products = db.get_products(limit=limit, search=search)
    return jsonify({'success': True, 'data': products})

@app.route('/api/products/low-stock', methods=['GET'])
def get_low_stock():
    threshold = request.args.get('threshold', 5, type=int)
    products = db.get_low_stock_products(threshold=threshold)
    return jsonify({'success': True, 'data': products, 'count': len(products)})

@app.route('/api/products/stats', methods=['GET'])
def get_product_stats():
    stats = db.get_product_stats()
    return jsonify({'success': True, 'data': stats})

# ===== ORDERS API =====
@app.route('/api/orders', methods=['GET'])
def get_orders():
    limit = request.args.get('limit', 50, type=int)
    status = request.args.get('status', None)
    orders = db.get_orders(limit=limit, status=status)
    return jsonify({'success': True, 'data': orders})

@app.route('/api/orders/stats', methods=['GET'])
def get_order_stats():
    stats = db.get_order_stats()
    return jsonify({'success': True, 'data': stats})

# ===== COUPONS API =====
@app.route('/api/coupons', methods=['GET'])
def get_coupons():
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    coupons = db.get_coupons(active_only=active_only)
    return jsonify({'success': True, 'data': coupons})

@app.route('/api/coupons/usage', methods=['GET'])
def get_coupon_usage():
    usage = db.get_coupon_usage()
    return jsonify({'success': True, 'data': usage})

# ===== SALES API =====
@app.route('/api/sales/analytics', methods=['GET'])
def get_sales_analytics():
    analytics = db.get_sales_analytics()
    return jsonify({'success': True, 'data': analytics})

@app.route('/api/sales/profit', methods=['GET'])
def get_profit_analysis():
    profit = db.get_profit_analysis()
    return jsonify({'success': True, 'data': profit})

# ===== USERS API =====
@app.route('/api/users', methods=['GET'])
def get_users():
    limit = request.args.get('limit', 50, type=int)
    users = db.get_users(limit=limit)
    return jsonify({'success': True, 'data': users})

@app.route('/api/users/top', methods=['GET'])
def get_top_customers():
    limit = request.args.get('limit', 10, type=int)
    customers = db.get_top_customers(limit=limit)
    return jsonify({'success': True, 'data': customers})

# ===== DASHBOARD SUMMARY =====
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_summary():
    try:
        product_stats = db.get_product_stats()
        order_stats = db.get_order_stats()
        sales_analytics = db.get_sales_analytics()
        profit_analysis = db.get_profit_analysis()
        recent_orders = db.get_orders(limit=5)
        low_stock = db.get_low_stock_products(threshold=5)
        top_customers = db.get_top_customers(limit=5)
        
        return jsonify({
            'success': True,
            'data': {
                'products': product_stats,
                'orders': order_stats,
                'sales': sales_analytics,
                'profit': profit_analysis,
                'recent_orders': recent_orders,
                'low_stock_products': low_stock,
                'top_customers': top_customers
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== HEALTH CHECK =====
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'ecommerce-mcp'})

# ===== PRODUCT OPERATIONS =====
@app.route('/api/products/<int:product_id>/price', methods=['PUT'])
def update_product_price(product_id):
    data = request.json
    if 'price' not in data:
        return jsonify({'success': False, 'error': 'price required'}), 400
    result = db.update_product_price(product_id, data['price'])
    return jsonify(result), (200 if result['success'] else 400)

@app.route('/api/products/<int:product_id>/stock', methods=['PUT'])
def update_product_stock(product_id):
    data = request.json
    if 'quantity' not in data:
        return jsonify({'success': False, 'error': 'quantity required'}), 400
    result = db.update_product_stock(product_id, data['quantity'])
    return jsonify(result), (200 if result['success'] else 400)

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    result = db.delete_product(product_id)
    return jsonify(result), (200 if result['success'] else 400)

# ===== COUPON OPERATIONS =====
@app.route('/api/coupons', methods=['POST'])
def create_coupon():
    data = request.json
    required = ['code', 'name', 'discount_type', 'discount_value']
    if not all(k in data for k in required):
        return jsonify({'success': False, 'error': f'Required fields: {required}'}), 400
    
    result = db.create_coupon(
        code=data['code'],
        name=data['name'],
        discount_type=data['discount_type'],
        discount_value=data['discount_value'],
        min_order=data.get('min_order', 0),
        max_uses=data.get('max_uses'),
        expiry_days=data.get('expiry_days', 30)
    )
    return jsonify(result), (201 if result['success'] else 400)

@app.route('/api/coupons/cleanup', methods=['POST'])
def delete_expired_coupons():
    result = db.delete_expired_coupons()
    return jsonify(result)

@app.route('/api/coupons/<int:coupon_id>/disable', methods=['PUT'])
def disable_coupon(coupon_id):
    result = db.disable_coupon(coupon_id)
    return jsonify(result), (200 if result['success'] else 400)

# ===== ORDER OPERATIONS =====
@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    if 'status' not in data:
        return jsonify({'success': False, 'error': 'status required'}), 400
    result = db.update_order_status(order_id, data['status'])
    return jsonify(result), (200 if result['success'] else 400)

@app.route('/api/orders/<int:order_id>/payment-status', methods=['PUT'])
def update_order_payment_status(order_id):
    data = request.json
    if 'payment_status' not in data:
        return jsonify({'success': False, 'error': 'payment_status required'}), 400
    result = db.update_order_payment_status(order_id, data['payment_status'])
    return jsonify(result), (200 if result['success'] else 400)

# ===== REPORTS =====
@app.route('/api/reports/sales', methods=['GET'])
def export_sales_report():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    result = db.export_sales_report(start_date, end_date)
    return jsonify(result)

@app.route('/api/reports/products', methods=['GET'])
def export_product_report():
    result = db.export_product_report()
    return jsonify(result)

# ===== ALERTS & MONITORING =====
@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    result = db.get_alerts()
    return jsonify(result)

# ===== MAINTENANCE =====
@app.route('/api/maintenance/backup', methods=['POST'])
def backup_database():
    result = db.backup_database()
    return jsonify(result)

@app.route('/api/maintenance/cleanup', methods=['POST'])
def cleanup_database():
    days = request.json.get('days', 30) if request.json else 30
    result = db.cleanup_old_logs(days)
    return jsonify(result)

# ===== HOME =====
from flask import send_file

@app.route('/', methods=['GET'])
def home():
    return send_file('dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
