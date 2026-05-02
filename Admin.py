from flask import Blueprint, render_template, request, redirect, session, jsonify
from email_utils import send_email
from db import db
from datetime import datetime
import pytz

admin_bp = Blueprint('admin', __name__)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Return current datetime in IST"""
    return datetime.now(IST)

def format_ist_datetime(dt):
    """Format datetime to IST string"""
    if dt is None:
        return '-'
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    return dt.astimezone(IST).strftime('%d-%m-%Y %H:%M:%S')

def format_ist_date(dt):
    """Format date to IST string"""
    if dt is None:
        return '-'
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    return dt.astimezone(IST).strftime('%d-%m-%Y')


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect('/admin/dashboard')
    
    msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session.permanent = True
            return redirect('/admin/dashboard')
        else:
            msg = "Invalid credentials"
    
    return render_template('Admin/admin_login.html', msg=msg)


@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin/login')


@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    stats = {'pending_sellers': 0, 'approved_sellers': 0, 'total_buyers': 0, 'total_orders': 0, 'total_products': 0}
    
    try:
        cur.execute("SELECT status, COUNT(*) FROM sellers GROUP BY status")
        for row in cur.fetchall():
            if row[0] == 'pending':
                stats['pending_sellers'] = row[1]
            elif row[0] == 'approved':
                stats['approved_sellers'] = row[1]
        
        cur.execute("SELECT COUNT(*) FROM buyers")
        result = cur.fetchone()
        stats['total_buyers'] = result[0] if result else 0
        
        cur.execute("SELECT COUNT(*) FROM orders")
        result = cur.fetchone()
        stats['total_orders'] = result[0] if result else 0
        
        cur.execute("SELECT COUNT(*) FROM products")
        result = cur.fetchone()
        stats['total_products'] = result[0] if result else 0
    except Exception as e:
        print(f"Admin dashboard error: {e}")
    finally:
        cur.close()
        conn.close()
    
    return render_template('Admin/admin_dashboard.html', stats=stats)


@admin_bp.route('/admin/seller/<int:seller_id>/approve')
def approve_seller(seller_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        ist_now = get_ist_now()
        cur.execute("UPDATE sellers SET status = 'approved', approved_at = %s WHERE id = %s", (ist_now, seller_id))
        conn.commit()
        cur.execute("SELECT email, name FROM sellers WHERE id = %s", (seller_id,))
        seller = cur.fetchone()

        
    except Exception as e:
        print(f"Approve seller error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return redirect('/admin/sellers')


@admin_bp.route('/admin/seller/<int:seller_id>/reject')
def reject_seller(seller_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("UPDATE sellers SET status = 'rejected' WHERE id = %s", (seller_id,))
        conn.commit()
        cur.execute("SELECT email, name FROM sellers WHERE id = %s", (seller_id,))
        seller = cur.fetchone()

        
    except Exception as e:
        print(f"Reject seller error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return redirect('/admin/sellers')


@admin_bp.route('/admin/sellers')
def all_sellers():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    all_sellers_list = []
    pending_sellers_list = []
    
    try:
        cur.execute("""
            SELECT id, username, name, email, phone, status, 
                   created_at,
                   approved_at
            FROM sellers 
            ORDER BY created_at DESC
        """)
        
        for row in cur.fetchall():
            seller = {
                'id': row[0],
                'username': row[1],
                'name': row[2],
                'email': row[3],
                'phone': row[4] or '-',
                'status': row[5],
                'created_at': format_ist_datetime(row[6]) if row[6] else '-',
                'approved_at': format_ist_datetime(row[7]) if row[7] else '-'
            }
            all_sellers_list.append(seller)
            
            if row[5] == 'pending':
                pending_sellers_list.append(seller)
        
    except Exception as e:
        print(f"Fetch sellers error: {e}")
    finally:
        cur.close()
        conn.close()
    
    return render_template('Admin/all_sellers.html', 
                          all_sellers=all_sellers_list,
                          pending_sellers=pending_sellers_list,
                          pending_sellers_count=len(pending_sellers_list))


@admin_bp.route('/admin/daily-payments')
def admin_daily_payments():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    sellers_data = []
    
    try:
        cur.execute("""
            SELECT id, name, username, email, phone 
            FROM sellers 
            WHERE status = 'approved'
            ORDER BY name
        """)
        sellers = cur.fetchall()
        
        for seller in sellers:
            seller_id, seller_name, seller_username, seller_email, seller_phone = seller
            
            # FIXED: Get order dates directly from orders table without timezone conversion
            cur.execute("""
                SELECT DISTINCT 
                    DATE(o.order_placed_at) as order_date
                FROM orders o
                WHERE o.seller_id = %s 
                    AND o.status IN ('pending', 'review_submitted', 'approved', 'paid')
                ORDER BY order_date DESC
            """, (seller_id,))
            
            order_dates = cur.fetchall()
            payment_list = []
            
            for date_row in order_dates:
                order_date = date_row[0]
                
                cur.execute("""
                    SELECT 
                        COUNT(*) as order_count,
                        SUM(o.order_amount) as total_amount
                    FROM orders o
                    WHERE o.seller_id = %s 
                        AND DATE(o.order_placed_at) = %s
                        AND o.status IN ('pending', 'review_submitted', 'approved', 'paid')
                """, (seller_id, order_date))
                
                order_stats = cur.fetchone()
                order_count = order_stats[0]
                total_amount = float(order_stats[1]) if order_stats[1] else 0
                
                cur.execute("""
                    SELECT id, status, paid_at
                    FROM daily_payments
                    WHERE seller_id = %s AND payment_date = %s
                """, (seller_id, order_date))
                
                payment_record = cur.fetchone()
                
                if payment_record:
                    payment_id = payment_record[0]
                    payment_status = payment_record[1]
                    paid_at = payment_record[2]
                else:
                    payment_id = None
                    payment_status = 'pending'
                    paid_at = None
                
                payment_list.append({
                    'payment_date': order_date.strftime('%d-%m-%Y') if order_date else '-',
                    'order_count': order_count,
                    'total_amount': total_amount,
                    'status': payment_status,  
                    'payment_id': payment_id,
                    'paid_at': format_ist_datetime(paid_at) if paid_at else '-'
                })
            
            if payment_list:
                sellers_data.append({
                    'id': seller_id,
                    'name': seller_name,
                    'username': seller_username,
                    'email': seller_email,
                    'phone': seller_phone or '-',
                    'payments': payment_list
                })
        
    except Exception as e:
        print(f"Admin daily payments error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()
    
    return render_template('Admin/daily_payments.html', sellers=sellers_data)


@admin_bp.route('/admin/api/orders-by-date')
def api_orders_by_date():
    """API to get orders for a specific seller and date"""
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    seller_id = request.args.get('seller_id')
    date = request.args.get('date')
    
    if not seller_id or not date:
        return jsonify({"error": "Missing parameters"}), 400
    
    from datetime import datetime
    date_obj = datetime.strptime(date, '%d-%m-%Y')
    date_db = date_obj.strftime('%Y-%m-%d')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        # FIXED: Removed timezone conversion, use direct DATE comparison
        cur.execute("""
            SELECT 
                o.id,
                o.order_id,
                o.product_name,
                o.order_amount,
                o.refund_amount,
                o.status,
                o.order_screenshot,
                o.delivered_screenshot,
                o.review_screenshot,
                o.review_link,
                b.name as buyer_name,
                b.email as buyer_email
            FROM orders o
            JOIN buyers b ON o.buyer_id = b.id
            WHERE o.seller_id = %s 
                AND DATE(o.order_placed_at) = %s
            ORDER BY o.id DESC
        """, (seller_id, date_db))
        
        orders = cur.fetchall()
        
        orders_list = []
        for order in orders:
            orders_list.append({
                "id": order[0],
                "order_id": order[1],
                "product_name": order[2],
                "order_amount": float(order[3]) if order[3] else 0,
                "refund_amount": float(order[4]) if order[4] else 0,
                "status": order[5],
                "order_screenshot": order[6],
                "delivered_screenshot": order[7],
                "review_screenshot": order[8],
                "review_link": order[9],
                "buyer_name": order[10],
                "buyer_email": order[11]
            })
        
        return jsonify({"orders": orders_list})
        
    except Exception as e:
        print(f"API orders by date error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@admin_bp.route('/admin/payment/<int:payment_id>/approve', methods=['POST'])
def approve_payment(payment_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        notes = request.form.get('notes', '')
        
        cur.execute("SELECT seller_id, payment_date FROM daily_payments WHERE id = %s", (payment_id,))
        payment = cur.fetchone()
        
        if not payment:
            return redirect('/admin/daily-payments')
        
        seller_id = payment[0]
        payment_date = payment[1]
        
        ist_now = get_ist_now()
        cur.execute("""
            UPDATE daily_payments 
            SET status = 'paid', paid_at = %s, notes = %s
            WHERE id = %s
        """, (ist_now, notes, payment_id))
        conn.commit()
        
        cur.execute("""
            UPDATE orders 
            SET status = 'paid', 
                paid_at = %s
            WHERE seller_id = %s 
            AND DATE(order_placed_at at time zone 'UTC' at time zone 'Asia/Kolkata') = %s
            AND status = 'approved'
        """, (ist_now, seller_id, payment_date))
        conn.commit()
        
        updated_count = cur.rowcount
        print(f"✅ Payment approved for seller {seller_id} on date {payment_date}, {updated_count} orders marked as paid")
        
    except Exception as e:
        print(f"Approve payment error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return redirect('/admin/daily-payments')


@admin_bp.route('/admin/payment/<int:payment_id>/reject', methods=['POST'])
def reject_payment(payment_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        notes = request.form.get('notes', '')
        cur.execute("UPDATE daily_payments SET status = 'rejected', notes = %s WHERE id = %s", (notes, payment_id))
        conn.commit()
    except Exception as e:
        print(f"Reject payment error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return redirect('/admin/daily-payments')


@admin_bp.route('/admin/payment/create', methods=['POST'])
def create_payment():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        seller_id = request.form.get('seller_id')
        payment_date = request.form.get('payment_date')
        total_amount = request.form.get('total_amount')
        order_count = request.form.get('order_count')
        
        from datetime import datetime
        date_obj = datetime.strptime(payment_date, '%d-%m-%Y')
        payment_date_db = date_obj.strftime('%Y-%m-%d')
        
        cur.execute("SELECT id FROM daily_payments WHERE seller_id=%s AND payment_date=%s", (seller_id, payment_date_db))
        existing = cur.fetchone()
        
        ist_now = get_ist_now()
        
        if existing:
            cur.execute("""
                UPDATE daily_payments 
                SET status = 'paid', paid_at = %s, notes = 'Marked as paid by admin'
                WHERE id = %s
            """, (ist_now, existing[0]))
        else:
            cur.execute("""
                INSERT INTO daily_payments (seller_id, payment_date, total_amount, order_count, status, paid_at, notes)
                VALUES (%s, %s, %s, %s, 'paid', %s, 'Marked as paid by admin')
            """, (seller_id, payment_date_db, total_amount, order_count, ist_now))
        
        conn.commit()
        
        cur.execute("""
            UPDATE orders 
            SET status = 'paid', 
                paid_at = %s
            WHERE seller_id = %s 
            AND DATE(order_placed_at at time zone 'UTC' at time zone 'Asia/Kolkata') = %s
            AND status = 'approved'
        """, (ist_now, seller_id, payment_date_db))
        conn.commit()
        
        updated_count = cur.rowcount
        print(f"✅ Payment marked as paid for seller {seller_id} on date {payment_date}, {updated_count} orders marked as paid")
        
    except Exception as e:
        print(f"Create payment error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return redirect('/admin/daily-payments')


@admin_bp.route('/admin/payment-history')
def admin_payment_history():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    sellers_data = []
    
    try:
        # Get all sellers who have payment batches
        cur.execute("""
            SELECT DISTINCT o.seller_id, s.name, s.username, s.email, s.phone
            FROM orders o
            JOIN sellers s ON o.seller_id = s.id
            WHERE o.batch_id IS NOT NULL
            ORDER BY s.name
        """)
        sellers = cur.fetchall()
        
        for seller in sellers:
            seller_id = seller[0]
            seller_name = seller[1]
            seller_username = seller[2]
            seller_email = seller[3]
            seller_phone = seller[4] or '-'
            
            # Get all batches for this seller
            cur.execute("""
                SELECT DISTINCT pb.id, pb.batch_id, pb.total_orders, pb.total_refund_amount, 
                       pb.status, pb.created_at, pb.processed_at
                FROM payment_batches pb
                WHERE pb.seller_id = %s
                ORDER BY pb.created_at DESC
            """, (seller_id,))
            batches = cur.fetchall()
            
            batch_list = []
            for b in batches:
                batch_id_value = b[1]
                
                # Get items for this batch - directly from orders table
                cur.execute("""
                    SELECT o.id, o.order_id, o.product_name, 
                           o.refund_amount, o.status
                    FROM orders o
                    WHERE o.batch_id = %s
                """, (batch_id_value,))
                items = cur.fetchall()
                
                item_list = []
                for item in items:
                    item_list.append({
                        "order_id": item[0],
                        "order_number": item[1],
                        "product_name": item[2],
                        "refund_amount": float(item[3]) if item[3] else 0,
                        "status": item[4] if item[4] else 'pending'
                    })
                
                batch_list.append({
                    "id": b[0],
                    "batch_id": batch_id_value,
                    "total_orders": b[2],
                    "total_refund_amount": float(b[3]) if b[3] else 0,
                    "status": b[4] if b[4] else 'pending',
                    "created_at": format_ist_datetime(b[5]) if b[5] else '-',
                    "processed_at": format_ist_datetime(b[6]) if b[6] else '-',
                    "order_items": item_list
                })
            
            if batch_list:
                sellers_data.append({
                    "id": seller_id,
                    "name": seller_name,
                    "username": seller_username,
                    "email": seller_email,
                    "phone": seller_phone,
                    "batches": batch_list
                })
        
    except Exception as e:
        print(f"Admin payment history error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return render_template('Admin/payment_history.html', sellers=sellers_data)


@admin_bp.route('/admin/payment-batch/<int:batch_id>/update-status', methods=['POST'])
def update_payment_batch_status(batch_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    if new_status not in ['pending', 'processing', 'completed', 'failed']:
        return jsonify({"error": "Invalid status"}), 400
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT batch_id FROM payment_batches WHERE id = %s", (batch_id,))
        result = cur.fetchone()
        
        if not result:
            return jsonify({"error": "Batch not found"}), 404
        
        batch_id_value = result[0]
        
        ist_now = get_ist_now()
        cur.execute("""
            UPDATE payment_batches 
            SET status = %s, 
                processed_at = CASE WHEN %s = 'completed' THEN %s ELSE processed_at END,
                notes = %s
            WHERE id = %s
        """, (new_status, new_status, ist_now, notes, batch_id))
        conn.commit()
        
        # If status is completed, update orders status to 'paid'
        if new_status == 'completed':
            cur.execute("""
                UPDATE orders 
                SET status = 'paid'
                WHERE batch_id = %s AND status = 'approved'
            """, (batch_id_value,))
            conn.commit()
            print(f"✅ Updated orders status to paid for batch: {batch_id_value}")
        
        print(f"✅ Batch {batch_id_value} status updated to {new_status}")
        
    except Exception as e:
        print(f"Update payment batch status error: {e}")
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    
    return redirect('/admin/payment-history')


@admin_bp.route('/admin/batch-refund')
def admin_batch_refund():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    batches_data = []
    
    try:
        cur.execute("""
            SELECT DISTINCT pb.id, pb.batch_id, pb.seller_id, pb.total_orders, 
                   pb.total_refund_amount, pb.status, pb.created_at, pb.processed_at, s.name as seller_name
            FROM payment_batches pb
            JOIN sellers s ON pb.seller_id = s.id
            ORDER BY pb.created_at DESC
        """)
        
        batches = cur.fetchall()
        
        for batch in batches:
            batch_id = batch[0]
            batch_id_value = batch[1]
            seller_id = batch[2]
            total_orders = batch[3]
            total_refund = batch[4]
            batch_status = batch[5]
            created_at = batch[6]
            processed_at = batch[7]
            seller_name = batch[8]
            
            # Get all orders in this batch - directly from orders table
            cur.execute("""
                SELECT o.id, o.order_id, o.product_name, 
                       o.refund_amount, o.status, b.name as buyer_name, b.email as buyer_email,
                       o.order_placed_at
                FROM orders o
                JOIN buyers b ON o.buyer_id = b.id
                WHERE o.batch_id = %s
            """, (batch_id_value,))
            
            items = cur.fetchall()
            
            if not items:
                continue
            
            item_list = []
            buyer_set = set()
            
            for item in items:
                buyer_set.add(item[5])
                item_list.append({
                    "order_id": item[0],
                    "order_number": item[1],
                    "product_name": item[2],
                    "refund_amount": float(item[3]) if item[3] else 0,
                    "status": item[4],
                    "buyer_name": item[5],
                    "buyer_email": item[6],
                    "order_date": format_ist_datetime(item[7]) if item[7] else '-'
                })
            
            batches_data.append({
                "id": batch_id,
                "batch_id": batch_id_value,
                "seller_id": seller_id,
                "seller_name": seller_name,
                "total_orders": total_orders,
                "total_refund_amount": float(total_refund) if total_refund else 0,
                "unique_buyers": len(buyer_set),
                "status": batch_status,
                "created_at": format_ist_datetime(created_at) if created_at else '-',
                "processed_at": format_ist_datetime(processed_at) if processed_at else '-',
                "order_items": item_list
            })
        
    except Exception as e:
        print(f"Admin batch refund error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()
    
    return render_template('Admin/batch_refund.html', batches=batches_data)


@admin_bp.route('/admin/batch-refund/mark-paid', methods=['POST'])
def mark_order_as_paid():
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    order_id = data.get('order_id')
    batch_id = data.get('batch_id')
    
    if not order_id:
        return jsonify({"error": "Order ID required"}), 400
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT id, refund_amount, buyer_id, order_id 
            FROM orders 
            WHERE id = %s AND status = 'approved'
        """, (order_id,))
        
        order = cur.fetchone()
        
        if not order:
            cur.execute("SELECT status FROM orders WHERE id = %s", (order_id,))
            existing = cur.fetchone()
            if existing and existing[0] == 'paid':
                return jsonify({"error": "Order already paid"}), 400
            return jsonify({"error": "Order not found or not approved"}), 404
        
        refund_amount = float(order[1]) if order[1] else 0
        buyer_amount = refund_amount / 2
        
        ist_now = get_ist_now()
        cur.execute("""
            UPDATE orders 
            SET status = 'paid', 
                paid_at = %s,
                buyer_refund_amount = %s
            WHERE id = %s
        """, (ist_now, buyer_amount, order_id))
        
        conn.commit()
        
        # Check if all orders in this batch are now paid
        cur.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE batch_id = %s AND status != 'paid'
        """, (batch_id,))
        
        pending_count = cur.fetchone()[0]
        
        # If no pending orders, update batch status to 'completed'
        if pending_count == 0 and batch_id:
            cur.execute("""
                UPDATE payment_batches 
                SET status = 'completed', 
                    processed_at = %s
                WHERE batch_id = %s
            """, (ist_now, batch_id))
            conn.commit()
        
        return jsonify({
            "success": True,
            "amount": f"₹{buyer_amount:,.2f}",
            "message": "Order marked as paid"
        })
        
    except Exception as e:
        print(f"Mark order as paid error: {e}")
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()
