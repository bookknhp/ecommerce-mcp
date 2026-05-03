import sqlite3
from datetime import datetime
from pathlib import Path
import os

# Use relative path for Railway compatibility
DB_PATH = Path(os.environ.get('DATABASE_PATH', './database.sqlite'))

class Database:
    def __init__(self):
        self.db_path = DB_PATH
    
    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    # ===== PRODUCTS =====
    def get_products(self, limit=50, search=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, name, price, stock_quantity, category_id, 
                   sold_count, view_count, is_promo, is_new, 
                   cost_price, created_at
            FROM products
        """
        
        if search:
            query += f" WHERE name LIKE '%{search}%'"
        
        query += f" LIMIT {limit}"
        cursor.execute(query)
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    def get_low_stock_products(self, threshold=5):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, price, stock_quantity, category_id, sold_count
            FROM products
            WHERE stock_quantity < ?
            ORDER BY stock_quantity ASC
        """, (threshold,))
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products
    
    def get_product_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_products,
                SUM(stock_quantity) as total_stock,
                SUM(sold_count) as total_sold,
                AVG(price) as avg_price,
                MAX(price) as max_price,
                MIN(price) as min_price
            FROM products
        """)
        
        stats = dict(cursor.fetchone())
        conn.close()
        return stats
    
    # ===== ORDERS =====
    def get_orders(self, limit=50, status=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT o.id, o.user_id, o.total_amount, o.status, 
                   o.payment_status, o.order_date, o.created_at,
                   u.name as user_name
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
        """
        
        if status:
            query += f" WHERE o.status = '{status}'"
        
        query += f" ORDER BY o.created_at DESC LIMIT {limit}"
        cursor.execute(query)
        
        orders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return orders
    
    def get_order_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
                COUNT(CASE WHEN payment_status = 'unpaid' THEN 1 END) as unpaid_orders
            FROM orders
        """)
        
        stats = dict(cursor.fetchone())
        conn.close()
        return stats
    
    # ===== COUPONS =====
    def get_coupons(self, active_only=True):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, code, name, discount_type, discount_value, 
                   min_order_value, max_total_uses, status, 
                   expiry_date, created_at
            FROM coupons
        """
        
        if active_only:
            query += " WHERE status = 'ACTIVE' AND expiry_date > datetime('now')"
        
        query += " ORDER BY created_at DESC"
        cursor.execute(query)
        
        coupons = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return coupons
    
    def get_coupon_usage(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, c.code, c.name, c.discount_value,
                   COUNT(oc.id) as usage_count,
                   SUM(oc.discount_amount) as total_discount
            FROM coupons c
            LEFT JOIN order_applied_coupons oc ON c.id = oc.coupon_id
            GROUP BY c.id
        """)
        
        usage = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return usage
    
    # ===== SALES & PROFIT =====
    def get_sales_analytics(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Net Revenue (Amount actually paid)
        cursor.execute("""
            SELECT 
                SUM(amount_paid) as netRevenue,
                SUM(discount_amount) as totalDiscounts,
                SUM(points_used) as totalPoints
            FROM orders 
            WHERE payment_status = 'paid' AND status != 'cancelled'
        """)
        rev_data = dict(cursor.fetchone() or {})
        
        net_revenue = float(rev_data.get('netRevenue') or 0)
        total_discounts = float(rev_data.get('totalDiscounts') or 0)
        total_points = float(rev_data.get('totalPoints') or 0)
        
        # Gross Sales Value (before any deductions)
        gross_sales = net_revenue + total_discounts + total_points
        
        return {
            'total_orders': self.get_order_stats()['total_orders'],
            'gross_sales_value': gross_sales,
            'net_revenue_from_sales': net_revenue,
            'total_discounts_given': total_discounts,
            'total_points_used': total_points
        }
    
    def get_profit_analysis(self):
        """Calculate profit using Admin's formula"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get revenue data
        cursor.execute("""
            SELECT 
                SUM(amount_paid) as netRevenue,
                SUM(discount_amount) as totalDiscounts,
                SUM(points_used) as totalPoints
            FROM orders 
            WHERE payment_status = 'paid' AND status != 'cancelled'
        """)
        rev_data = dict(cursor.fetchone() or {})
        net_revenue = float(rev_data.get('netRevenue') or 0)
        
        # Get expenses (per Admin formula)
        cursor.execute("""
            SELECT 
                SUM(oi.quantity * p.cost_price) as sumProductCost,
                SUM(oi.quantity * p.marketing_cost) as sumMarketingCost,
                SUM(oi.quantity * p.shipping_cost) as sumShippingCost,
                SUM(oi.quantity * p.operating_cost) as sumOperatingCost,
                SUM(oi.quantity * p.commission_1) as sumCommission,
                SUM(oi.quantity * (oi.price_at_purchase * p.platform_fee / 100)) as sumPlatformFee,
                SUM(oi.quantity * (oi.price_at_purchase * p.vat_percent / 100)) as sumVat
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.payment_status = 'paid' AND o.status != 'cancelled'
        """)
        expense_data = dict(cursor.fetchone() or {})
        
        # Calculate totals
        product_cost = float(expense_data.get('sumProductCost') or 0)
        marketing_cost = float(expense_data.get('sumMarketingCost') or 0)
        shipping_cost = float(expense_data.get('sumShippingCost') or 0)
        operating_cost = float(expense_data.get('sumOperatingCost') or 0)
        commission = float(expense_data.get('sumCommission') or 0)
        platform_fee = float(expense_data.get('sumPlatformFee') or 0)
        vat = float(expense_data.get('sumVat') or 0)
        
        # Total outflow (money that leaves)
        total_outflow = product_cost + marketing_cost + shipping_cost + operating_cost + commission + vat
        
        # Net Profit
        net_profit = net_revenue - total_outflow
        profit_margin = (net_profit / net_revenue * 100) if net_revenue > 0 else 0
        
        conn.close()
        
        return {
            'net_revenue': net_revenue,
            'product_cost': product_cost,
            'marketing_cost': marketing_cost,
            'shipping_cost': shipping_cost,
            'operating_cost': operating_cost,
            'commission': commission,
            'vat': vat,
            'total_outflow': total_outflow,
            'net_profit': net_profit,
            'profit_margin_percent': profit_margin,
            'platform_income': platform_fee
        }
    
    # ===== USERS =====
    def get_users(self, limit=50):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT id, name, email, phone, created_at,
                   (SELECT COUNT(*) FROM orders WHERE user_id = users.id) as total_orders,
                   (SELECT SUM(total_amount) FROM orders WHERE user_id = users.id) as lifetime_value
            FROM users
            ORDER BY created_at DESC
            LIMIT {limit}
        """)
        
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    
    def get_top_customers(self, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT u.id, u.name, u.email,
                   COUNT(o.id) as order_count,
                   SUM(o.total_amount) as total_spent
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id
            ORDER BY total_spent DESC
            LIMIT {limit}
        """)
        
        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return customers
    
    # ===== WRITE OPERATIONS =====
    
    # PRODUCTS
    def update_product_price(self, product_id, new_price):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products SET price = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (new_price, product_id))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return {'success': success, 'message': f'Product {product_id} price updated to ฿{new_price}' if success else 'Product not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_product_stock(self, product_id, quantity):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products SET stock_quantity = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (quantity, product_id))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return {'success': success, 'message': f'Product {product_id} stock updated to {quantity}' if success else 'Product not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_product(self, product_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Check if product has orders
            cursor.execute("SELECT COUNT(*) as count FROM order_items WHERE product_id = ?", (product_id,))
            order_count = cursor.fetchone()[0]
            if order_count > 0:
                conn.close()
                return {'success': False, 'error': f'Cannot delete: Product has {order_count} orders'}
            
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return {'success': success, 'message': f'Product {product_id} deleted' if success else 'Product not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # COUPONS
    def create_coupon(self, code, name, discount_type, discount_value, min_order=0, max_uses=None, expiry_days=30):
        try:
            from datetime import datetime, timedelta
            conn = self.get_connection()
            cursor = conn.cursor()
            
            expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()
            
            cursor.execute("""
                INSERT INTO coupons 
                (code, name, discount_type, discount_value, min_order_value, max_total_uses, expiry_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
            """, (code, name, discount_type, discount_value, min_order, max_uses, expiry_date))
            
            conn.commit()
            coupon_id = cursor.lastrowid
            conn.close()
            return {'success': True, 'coupon_id': coupon_id, 'message': f'Coupon {code} created'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_expired_coupons(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE coupons SET status = 'EXPIRED'
                WHERE expiry_date < datetime('now') AND status = 'ACTIVE'
            """)
            conn.commit()
            deleted_count = cursor.rowcount
            conn.close()
            return {'success': True, 'deleted_count': deleted_count, 'message': f'Marked {deleted_count} coupons as expired'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def disable_coupon(self, coupon_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE coupons SET status = 'INACTIVE' WHERE id = ?", (coupon_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return {'success': success, 'message': f'Coupon {coupon_id} disabled' if success else 'Coupon not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ORDERS
    def update_order_status(self, order_id, status):
        try:
            valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
            if status not in valid_statuses:
                return {'success': False, 'error': f'Invalid status. Valid: {valid_statuses}'}
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?", (status, order_id))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return {'success': success, 'message': f'Order {order_id} status updated to {status}' if success else 'Order not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_order_payment_status(self, order_id, payment_status):
        try:
            valid_statuses = ['unpaid', 'paid', 'refunded']
            if payment_status not in valid_statuses:
                return {'success': False, 'error': f'Invalid status. Valid: {valid_statuses}'}
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET payment_status = ?, updated_at = datetime('now') WHERE id = ?", (payment_status, order_id))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return {'success': success, 'message': f'Order {order_id} payment status updated to {payment_status}' if success else 'Order not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # REPORTING & ANALYTICS
    def export_sales_report(self, start_date=None, end_date=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT o.id as order_id, o.order_date, u.name as customer,
                       o.total_amount, o.discount_amount, o.amount_paid,
                       o.status, o.payment_status
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                WHERE 1=1
            """
            
            params = []
            if start_date:
                query += " AND o.order_date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND o.order_date <= ?"
                params.append(end_date)
            
            query += " ORDER BY o.order_date DESC"
            
            cursor.execute(query, params)
            report = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return {'success': True, 'data': report, 'count': len(report)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_product_report(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, category_id, price, cost_price, stock_quantity,
                       sold_count, view_count, (price - cost_price) as profit_per_unit,
                       ((price - cost_price) * sold_count) as total_profit
                FROM products
                ORDER BY total_profit DESC
            """)
            
            report = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return {'success': True, 'data': report, 'count': len(report)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ALERTS & NOTIFICATIONS
    def get_alerts(self):
        """Generate system alerts"""
        try:
            alerts = []
            
            # Low stock products
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM products WHERE stock_quantity < 5")
            low_stock = cursor.fetchone()[0]
            if low_stock > 0:
                alerts.append({'type': 'LOW_STOCK', 'severity': 'HIGH', 'message': f'{low_stock} products have low stock'})
            
            # Unpaid orders
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE payment_status = 'unpaid' AND status != 'cancelled'")
            unpaid = cursor.fetchone()[0]
            if unpaid > 0:
                alerts.append({'type': 'UNPAID_ORDERS', 'severity': 'MEDIUM', 'message': f'{unpaid} orders waiting for payment'})
            
            # Expired coupons
            cursor.execute("SELECT COUNT(*) as count FROM coupons WHERE expiry_date < datetime('now') AND status = 'ACTIVE'")
            expired = cursor.fetchone()[0]
            if expired > 0:
                alerts.append({'type': 'EXPIRED_COUPONS', 'severity': 'LOW', 'message': f'{expired} coupons have expired'})
            
            conn.close()
            return {'success': True, 'alerts': alerts, 'count': len(alerts)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # DATABASE MAINTENANCE
    def backup_database(self):
        """Create database backup"""
        try:
            import shutil
            from datetime import datetime
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"/Users/bookk/Documents/FULL_BACKUP_20260503_0050/data/backups/shop_main_backup_{timestamp}.sqlite"
            
            shutil.copy2(str(self.db_path), backup_path)
            return {'success': True, 'backup_path': backup_path, 'message': f'Database backed up to {backup_path}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cleanup_old_logs(self, days=30):
        """Clean up old records"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete old email logs
            cursor.execute("""
                DELETE FROM email_logs 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            """, (days,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return {'success': True, 'deleted_count': deleted_count, 'message': f'Deleted logs older than {days} days'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
