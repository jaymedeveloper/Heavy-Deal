from flask import Blueprint, render_template, request, redirect, session, jsonify
from email_utils import send_email
from db import db

admin_bp = Blueprint('admin', __name__)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
    
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
        cur.execute("UPDATE sellers SET status = 'approved', approved_at = CURRENT_TIMESTAMP WHERE id = %s", (seller_id,))
        conn.commit()
        cur.execute("SELECT email, name FROM sellers WHERE id = %s", (seller_id,))
        seller=cur.fetchone()

        # ✅ Send approval email to seller
        send_email(
            to_email=seller[0],
            subject="Seller Account Approved - HeavyDeals",
            message=f"Dear {seller[1]},\n\nYour seller account has been approved. You can now login and start listing products.\n\nLogin here: https://heavy-deal-a5in.onrender.com/seller/login"
        )
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
        seller=cur.fetchone()

        # ✅ Send approval email to seller
        send_email(
            to_email=seller[0],
            subject="Seller Account Rejected - HeavyDeals",
            message=f"Dear {seller[1]},\n\nYour seller account has been Rejected. You can not use seller penal. \n\nSite: https://heavy-deal-a5in.onrender.com"
        )
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
        # Get all sellers
        cur.execute("""
            SELECT id, username, name, email, phone, status, 
                   TO_CHAR(created_at, 'DD-MM-YYYY') as created_at,
                   TO_CHAR(approved_at, 'DD-MM-YYYY') as approved_at
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
                'created_at': row[6] or '-',
                'approved_at': row[7] or '-'
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
        # Get all approved sellers with phone number
        cur.execute("""
            SELECT id, name, username, email, phone 
            FROM sellers 
            WHERE status = 'approved'
            ORDER BY name
        """)
        sellers = cur.fetchall()
        
        for seller in sellers:
            seller_id, seller_name, seller_username, seller_email, seller_phone = seller
            
            # Get all orders for this seller grouped by date
            cur.execute("""
                SELECT 
                    DATE(o.order_placed_at) as order_date,
                    COUNT(*) as order_count,
                    SUM(o.order_amount) as total_amount,
                    COALESCE(dp.status, 'pending') as payment_status,  
                    dp.id as payment_id,
                    dp.paid_at
                FROM orders o
                LEFT JOIN daily_payments dp ON dp.seller_id = o.seller_id AND DATE(dp.payment_date) = DATE(o.order_placed_at)
                WHERE o.seller_id = %s AND o.status IN ('pending', 'review_submitted', 'approved')
                GROUP BY DATE(o.order_placed_at), dp.status, dp.id, dp.paid_at
                ORDER BY order_date DESC
            """, (seller_id,))
            
            payments = cur.fetchall()
            payment_list = []
            
            for p in payments:
                order_date = p[0]
                order_count = p[1]
                total_amount = float(p[2]) if p[2] else 0
                payment_status = p[3] if p[3] else 'pending'  
                payment_id = p[4]
                paid_at = p[5].strftime('%d-%m-%Y %H:%M') if p[5] else '-'
                
                payment_list.append({
                    'payment_date': order_date.strftime('%d-%m-%Y') if order_date else '-',
                    'order_count': order_count,
                    'total_amount': total_amount,
                    'status': payment_status,  
                    'payment_id': payment_id,
                    'paid_at': paid_at
                })
            
            # Only add seller if they have orders
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
    finally:
        cur.close()
        conn.close()
    
    return render_template('Admin/daily_payments.html', sellers=sellers_data)


@admin_bp.route('/admin/payment/<int:payment_id>/approve', methods=['POST'])
def approve_payment(payment_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        notes = request.form.get('notes', '')
        
        # Get payment details first
        cur.execute("SELECT seller_id, payment_date FROM daily_payments WHERE id = %s", (payment_id,))
        payment = cur.fetchone()
        
        if not payment:
            return redirect('/admin/daily-payments')
        
        seller_id = payment[0]
        payment_date = payment[1]
        
        # Update daily_payments table
        cur.execute("""
            UPDATE daily_payments 
            SET status = 'paid', paid_at = CURRENT_TIMESTAMP, notes = %s
            WHERE id = %s
        """, (notes, payment_id))
        conn.commit()
        
        # ✅ Update order status from 'approved' to 'paid'
        cur.execute("""
            UPDATE orders 
            SET status = 'paid', 
                paid_at = CURRENT_TIMESTAMP
            WHERE seller_id = %s 
            AND DATE(order_placed_at) = %s
            AND status = 'approved'
        """, (seller_id, payment_date))
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
        
        # Convert date from DD-MM-YYYY to YYYY-MM-DD
        from datetime import datetime
        date_obj = datetime.strptime(payment_date, '%d-%m-%Y')
        payment_date_db = date_obj.strftime('%Y-%m-%d')
        
        # Check if payment already exists
        cur.execute("SELECT id FROM daily_payments WHERE seller_id=%s AND payment_date=%s", (seller_id, payment_date_db))
        existing = cur.fetchone()
        
        if existing:
            # Update existing to paid
            cur.execute("""
                UPDATE daily_payments 
                SET status = 'paid', paid_at = CURRENT_TIMESTAMP, notes = 'Marked as paid by admin'
                WHERE id = %s
            """, (existing[0],))
        else:
            # Create new payment record
            cur.execute("""
                INSERT INTO daily_payments (seller_id, payment_date, total_amount, order_count, status, paid_at, notes)
                VALUES (%s, %s, %s, %s, 'paid', CURRENT_TIMESTAMP, 'Marked as paid by admin')
            """, (seller_id, payment_date_db, total_amount, order_count))
        
        conn.commit()
        
        # ✅ Update order status from 'approved' to 'paid'
        cur.execute("""
            UPDATE orders 
            SET status = 'paid', 
                paid_at = CURRENT_TIMESTAMP
            WHERE seller_id = %s 
            AND DATE(order_placed_at) = %s
            AND status = 'approved'
        """, (seller_id, payment_date_db))
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
        # Check what columns exist in payment_batch_items table
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'payment_batch_items'
        """)
        columns = [col[0] for col in cur.fetchall()]
        
        # Determine which column name to use for batch reference
        batch_ref_column = None
        if 'batch_id' in columns:
            batch_ref_column = 'batch_id'
        
        else:
            return render_template('Admin/payment_history.html', sellers=[])
        
        # Get all sellers who have payment batches with phone number
        cur.execute("""
            SELECT DISTINCT pb.seller_id, s.name, s.username, s.email, s.phone
            FROM payment_batches pb
            JOIN sellers s ON pb.seller_id = s.id
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
                SELECT pb.id, pb.batch_id, pb.total_orders, pb.total_refund_amount, 
                       pb.status, pb.created_at, pb.processed_at
                FROM payment_batches pb
                WHERE pb.seller_id = %s
                ORDER BY pb.created_at DESC
            """, (seller_id,))
            batches = cur.fetchall()
            
            batch_list = []
            for b in batches:
                batch_id_value = b[1]
                
                # Get items for this batch
                query = f"""
                    SELECT pbi.order_id, o.order_id as order_number, o.product_name, 
                           pbi.order_refund_amount, pbi.status
                    FROM payment_batch_items pbi
                    JOIN orders o ON pbi.order_id = o.id
                    WHERE pbi.{batch_ref_column} = %s
                """
                
                cur.execute(query, (batch_id_value,))
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
                    "created_at": b[5].strftime('%d-%m-%Y %H:%M') if b[5] else '-',
                    "processed_at": b[6].strftime('%d-%m-%Y %H:%M') if b[6] else '-',
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
        # Get the batch_id_value
        cur.execute("SELECT batch_id FROM payment_batches WHERE id = %s", (batch_id,))
        result = cur.fetchone()
        
        if not result:
            return jsonify({"error": "Batch not found"}), 404
        
        batch_id_value = result[0]
        
        # Update payment_batches table
        cur.execute("""
            UPDATE payment_batches 
            SET status = %s, 
                processed_at = CASE WHEN %s = 'completed' THEN CURRENT_TIMESTAMP ELSE processed_at END,
                notes = %s
            WHERE id = %s
        """, (new_status, new_status, notes, batch_id))
        conn.commit()
        
        # If status is completed, also update payment_batch_items
        if new_status == 'completed':
            cur.execute("""
                UPDATE payment_batch_items 
                SET status = 'paid'
                WHERE batch_id = %s
            """, (batch_id_value,))
            conn.commit()
            print(f"✅ Updated payment_batch_items status to paid for batch: {batch_id_value}")
        
        print(f"✅ Batch {batch_id_value} status updated to {new_status}")
        
    except Exception as e:
        print(f"Update payment batch status error: {e}")
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    
    return redirect('/admin/payment-history')


# ✅ ONLY ONE admin_batch_refund function - DUPLICATE REMOVED
@admin_bp.route('/admin/batch-refund')
def admin_batch_refund():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    conn = db()
    cur = conn.cursor()
    batches_data = []
    
    try:
        # Get ALL payment batches (including completed)
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
            
            # Get all orders in this batch
            cur.execute("""
                SELECT pbi.order_id, o.order_id as order_number, o.product_name, 
                       o.refund_amount, o.status, b.name as buyer_name, b.email as buyer_email,
                       o.order_placed_at
                FROM payment_batch_items pbi
                JOIN orders o ON pbi.order_id = o.id
                JOIN buyers b ON o.buyer_id = b.id
                WHERE pbi.batch_id = %s
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
                    "order_date": item[7].strftime('%d-%m-%Y') if item[7] else '-'
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
                "created_at": created_at.strftime('%d-%m-%Y %H:%M') if created_at else '-',
                "processed_at": processed_at.strftime('%d-%m-%Y %H:%M') if processed_at else '-',
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
        # Check for 'approved' status
        cur.execute("""
            SELECT id, refund_amount, buyer_id, order_id 
            FROM orders 
            WHERE id = %s AND status = 'approved'
        """, (order_id,))
        
        order = cur.fetchone()
        
        if not order:
            # Check if already paid
            cur.execute("SELECT status FROM orders WHERE id = %s", (order_id,))
            existing = cur.fetchone()
            if existing and existing[0] == 'paid':
                return jsonify({"error": "Order already paid"}), 400
            return jsonify({"error": "Order not found or not approved"}), 404
        
        refund_amount = float(order[1]) if order[1] else 0
        buyer_amount = refund_amount / 2  # 50% to buyer
        
        # Update order status to 'paid'
        cur.execute("""
            UPDATE orders 
            SET status = 'paid', 
                paid_at = CURRENT_TIMESTAMP,
                buyer_refund_amount = %s
            WHERE id = %s
        """, (buyer_amount, order_id))
        
        conn.commit()
        
        # Check if all orders in this batch are now paid
        cur.execute("""
            SELECT COUNT(*) FROM payment_batch_items pbi
            JOIN orders o ON pbi.order_id = o.id
            WHERE pbi.batch_id = %s AND o.status != 'paid'
        """, (batch_id,))
        
        pending_count = cur.fetchone()[0]
        
        # If no pending orders, update batch status to 'completed'
        if pending_count == 0 and batch_id:
            cur.execute("""
                UPDATE payment_batches 
                SET status = 'completed', 
                    processed_at = CURRENT_TIMESTAMP
                WHERE batch_id = %s
            """, (batch_id,))
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
