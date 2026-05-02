from flask import Blueprint, render_template, request, redirect, session, jsonify
from db import db
import re
from datetime import datetime
import pytz

seller_bp = Blueprint('seller', __name__)

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')


@seller_bp.route("/seller/register", methods=['GET', 'POST'])
def seller_register():
    if session.get("seller_id"):
        return redirect("/seller/dashboard")
    
    msg = ""
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        email = request.form.get("email")
        phone = request.form.get("phone")
        name = request.form.get("name")
        
        if not all([username, password, email, name]):
            msg = "Please fill all required fields"
        elif password != confirm_password:
            msg = "Passwords do not match"
        elif len(password) < 6:
            msg = "Password must be at least 6 characters"
        elif not re.match(r'^[^\s@]+@([^\s@.,]+\.)+[^\s@.,]{2,}$', email):
            msg = "Invalid email format"
        else:
            conn = db()
            cur = conn.cursor()
            try:
                cur.execute("SELECT id FROM sellers WHERE username=%s OR email=%s", (username, email))
                if cur.fetchone():
                    msg = "Username or Email already exists"
                else:
                    cur.execute("INSERT INTO sellers (username, pass, name, email, phone, status) VALUES (%s, %s, %s, %s, %s, 'pending')",
                                (username, password, name, email, phone))
                    conn.commit()
                    return render_template("Seller/seller_pending.html", email=email)
            except Exception as e:
                print(f"Registration error: {e}")
                conn.rollback()
                msg = "Something went wrong"
            finally:
                cur.close()
                conn.close()
    
    return render_template("Seller/seller_register.html", msg=msg)


@seller_bp.route("/seller/login", methods=['GET', 'POST'])
def seller_login():
    if session.get("seller_id"):
        return redirect("/seller/dashboard")
    
    msg = ""
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = db()
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, name, status FROM sellers WHERE username=%s AND pass=%s", (username, password))
            data = cur.fetchone()
            
            if data:
                seller_id, seller_name, status = data
                if status == 'approved':
                    session["seller_id"] = seller_id
                    session["seller_name"] = seller_name
                    session.permanent = True
                    return redirect("/seller/dashboard")
                elif status == 'pending':
                    msg = "Your account is pending admin approval"
                elif status == 'rejected':
                    msg = "Your registration was rejected"
            else:
                msg = "Invalid Username or Password"
        except Exception as e:
            print(f"Login error: {e}")
            msg = "Something went wrong"
        finally:
            cur.close()
            conn.close()
    
    return render_template("Seller/seller_login.html", msg=msg)


@seller_bp.route("/seller/dashboard")
def seller_dashboard():
    if not session.get("seller_id"):
        return redirect("/seller/login")
    
    seller_id = session.get("seller_id")
    seller_name = session.get("seller_name")
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT status FROM sellers WHERE id=%s", (seller_id,))
        status = cur.fetchone()
        if status and status[0] != 'approved':
            session.clear()
            return redirect("/seller/login?msg=Account+not+approved")
    except Exception as e:
        print(f"Dashboard auth error: {e}")
    finally:
        cur.close()
        conn.close()
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT COUNT(*) FROM orders WHERE seller_id = %s", (seller_id,))
        total_orders = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM orders WHERE seller_id = %s AND status = 'approved'", (seller_id,))
        approved_orders = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COUNT(*) FROM orders WHERE seller_id = %s AND status = 'pending'", (seller_id,))
        pending_orders = cur.fetchone()[0] or 0
        
        cur.execute("SELECT COALESCE(SUM(refund_amount), 0) FROM orders WHERE seller_id = %s AND status = 'approved'", (seller_id,))
        total_amount = cur.fetchone()[0] or 0
    except Exception as e:
        print(f"Dashboard error: {e}")
        total_orders = approved_orders = pending_orders = total_amount = 0
    finally:
        cur.close()
        conn.close()
    
    return render_template("Seller/seller_dashboard.html", seller_name=seller_name,
                          total_orders=total_orders, approved_orders=approved_orders,
                          pending_orders=pending_orders, total_amount=total_amount)


@seller_bp.route("/seller/products")
def seller_products():
    if not session.get("seller_id"):
        return redirect("/seller/login")
    
    seller_id = session.get("seller_id")
    seller_name = session.get("seller_name")
    
    conn = db()
    cur = conn.cursor()
    products = []
    
    try:
        cur.execute("""
            SELECT p.id, p.name, p.brand, p.refund, p.order_limit, p.link,
                   COALESCE(COUNT(o.id), 0) as ordered_count
            FROM products p
            LEFT JOIN orders o ON p.id = o.product_id AND o.seller_id = p.seller_id
            WHERE p.seller_id = %s
            GROUP BY p.id, p.name, p.brand, p.refund, p.order_limit, p.link
            ORDER BY p.id DESC
        """, (seller_id,))
        
        rows = cur.fetchall()
        for r in rows:
            products.append({
                "id": r[0],
                "name": r[1],
                "brand": r[2],
                "refund": r[3],
                "order_limit": r[4],
                "link": r[5],
                "ordered_count": r[6] or 0
            })
    except Exception as e:
        print(f"Products fetch error: {e}")
    finally:
        cur.close()
        conn.close()
    
    return render_template("Seller/seller_products.html", seller_name=seller_name, products=products)


@seller_bp.route("/seller/products/add", methods=["POST"])
def add_product():
    if not session.get("seller_id"):
        return redirect("/seller/login")
    
    name = request.form.get("name")
    link = request.form.get("link")
    refund = request.form.get("refund")
    brand = request.form.get("brand")
    limit = request.form.get("limit")
    seller_id = session.get("seller_id")
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("INSERT INTO products (name, link, refund, brand, order_limit, seller_id) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, link, refund, brand, limit, seller_id))
        conn.commit()
    except Exception as e:
        print(f"Add product error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return redirect("/seller/products")


@seller_bp.route("/seller/orders")
def seller_orders():
    if not session.get("seller_id"):
        return redirect("/seller/login")
    
    seller_id = session.get("seller_id")
    seller_name = session.get("seller_name")
    
    conn = db()
    cur = conn.cursor()
    orders = []
    
    try:
        cur.execute("SET timezone = 'Asia/Kolkata'")
        
        cur.execute("""
            SELECT payment_date, status 
            FROM daily_payments 
            WHERE seller_id = %s
        """, (seller_id,))
        
        daily_payment_status = {}
        for row in cur.fetchall():
            if row[0]:
                payment_date = row[0].strftime('%d-%m-%Y')
                daily_payment_status[payment_date] = row[1]
        
        cur.execute("""
            SELECT o.id, o.order_id, o.product_name, o.order_amount, o.status, 
                   o.order_placed_at as order_placed_ist,
                   b.name, o.refund_amount, o.order_screenshot, o.delivered_screenshot, 
                   o.review_screenshot, o.review_link, o.batch_id
            FROM orders o 
            JOIN buyers b ON o.buyer_id = b.id
            WHERE o.seller_id = %s 
            ORDER BY o.id DESC
        """, (seller_id,))
        
        for r in cur.fetchall():
            order_date = ""
            if r[5]:
                # r[5] is order_placed_at (datetime object)
                order_date = r[5].strftime('%d-%m-%Y')
            
            orders.append({
                "id": r[0],
                "order_id": r[1],
                "product_name": r[2],
                "order_amount": r[3],
                "status": r[4],
                "order_placed_at": order_date,  # This will be DD-MM-YYYY
                "buyer_name": r[6],
                "refund_amount": r[7],
                "order_screenshot": r[8],
                "delivered_screenshot": r[9],
                "review_screenshot": r[10],
                "review_link": r[11],
                "batch_id": r[12] if len(r) > 12 else None,
                "daily_payment_status": daily_payment_status.get(order_date, 'pending')
            })
    except Exception as e:
        print(f"Orders fetch error: {e}")
    finally:
        cur.close()
        conn.close()
    
    return render_template("Seller/seller_orders.html", orders=orders, seller_name=seller_name)


@seller_bp.route("/seller/review-requests")
def seller_review_requests():
    if not session.get("seller_id"):
        return redirect("/seller/login")
    
    seller_id = session.get("seller_id")
    seller_name = session.get("seller_name")
    
    conn = db()
    cur = conn.cursor()
    reviews = []
    
    try:
        cur.execute("""
            SELECT o.id, o.order_id, o.product_name, o.order_amount, o.review_screenshot, o.review_link, 
                   b.name, o.refund_amount, o.order_screenshot, o.delivered_screenshot
            FROM orders o 
            JOIN buyers b ON o.buyer_id = b.id
            WHERE o.seller_id = %s AND o.status = 'review_submitted' 
            ORDER BY o.id DESC
        """, (seller_id,))
        
        for r in cur.fetchall():
            reviews.append({
                "id": r[0],
                "order_id": r[1],
                "product_name": r[2],
                "order_amount": r[3],
                "review_screenshot": r[4],
                "review_link": r[5],
                "buyer_name": r[6],
                "refund_amount": r[7],
                "order_screenshot": r[8],
                "delivered_screenshot": r[9]
            })
    except Exception as e:
        print(f"Review requests error: {e}")
    finally:
        cur.close()
        conn.close()
    
    return render_template("Seller/seller_review_requests.html", reviews=reviews, seller_name=seller_name)


@seller_bp.route("/seller/bulk-review-action", methods=['POST'])
def bulk_review_action():
    if not session.get("seller_id"):
        return jsonify({"error": "Unauthorized"}), 401
    
    seller_id = session.get("seller_id")
    seller_name = session.get("seller_name")
    
    data = request.get_json()
    if not data or 'actions' not in data:
        return jsonify({"error": "No actions provided"}), 400
    
    actions = data['actions']
    results = []
    approved_orders = []
    rejected_orders = []
    
    conn = db()
    cur = conn.cursor()
    
    import uuid
    batch_id = str(uuid.uuid4())[:8].upper()
    
    try:
        for action in actions:
            order_id = action.get('order_id')
            action_type = action.get('action')
            rejection_reason = action.get('reason', '')
            
            cur.execute("SELECT id, refund_amount, order_id, product_name FROM orders WHERE id=%s AND seller_id=%s AND status='review_submitted'", (order_id, seller_id))
            order = cur.fetchone()
            
            if not order:
                results.append({"order_id": order_id, "status": "failed", "reason": "Order not found or already processed"})
                continue
            
            if action_type == 'approve':
                refund_amount = float(order[1]) if order[1] else 0
                
                # Update order status to approved and set batch_id
                cur.execute("UPDATE orders SET status = 'approved', approved_at = CURRENT_TIMESTAMP, batch_id = %s WHERE id = %s", (batch_id, order_id))
                
                approved_orders.append({
                    "order_id": order_id,
                    "refund_amount": refund_amount
                })
                results.append({"order_id": order_id, "status": "approved"})
                
            elif action_type == 'reject':
                if not rejection_reason:
                    results.append({"order_id": order_id, "status": "failed", "reason": "Rejection reason required"})
                    continue
                cur.execute("""
                    UPDATE orders 
                    SET status = 'rejected', 
                        rejection_reason = %s, 
                        rejected_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (rejection_reason, order_id))
                rejected_orders.append(order_id)
                results.append({"order_id": order_id, "status": "rejected"})
        
        if approved_orders:
            total_refund = sum(o['refund_amount'] for o in approved_orders)
            total_orders_count = len(approved_orders)
            
            cur.execute("""
                INSERT INTO payment_batches (batch_id, seller_id, seller_name, total_orders, 
                    total_refund_amount, status, created_at)
                VALUES (%s, %s, %s, %s, %s, 'pending', CURRENT_TIMESTAMP)
            """, (batch_id, seller_id, seller_name, total_orders_count, total_refund))
            
            # No need to insert into payment_batch_items - batch_id already set in orders
            conn.commit()
        
    except Exception as e:
        print(f"Bulk review action error: {e}")
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()
    
    return jsonify({
        "results": results, 
        "success": True,
        "batch_id": batch_id if approved_orders else None,
        "approved_count": len(approved_orders),
        "rejected_count": len(rejected_orders)
    })


@seller_bp.route("/seller/approve-review/<int:order_id>")
def approve_review(order_id):
    if not session.get("seller_id"):
        return redirect("/seller/login")
    
    seller_id = session.get("seller_id")
    seller_name = session.get("seller_name")
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT refund_amount FROM orders WHERE id=%s AND seller_id=%s AND status='review_submitted'", (order_id, seller_id))
        order = cur.fetchone()
        
        if order:
            refund_amount = float(order[0]) if order[0] else 0
            
            import uuid
            batch_id = str(uuid.uuid4())[:8].upper()
            
            cur.execute("UPDATE orders SET status = 'approved', approved_at = CURRENT_TIMESTAMP, batch_id = %s WHERE id = %s", (batch_id, order_id))
            
            cur.execute("""
                INSERT INTO payment_batches (batch_id, seller_id, seller_name, total_orders, 
                    total_refund_amount, status, created_at)
                VALUES (%s, %s, %s, %s, %s, 'pending', CURRENT_TIMESTAMP)
            """, (batch_id, seller_id, seller_name, 1, refund_amount))
            
            conn.commit()
    except Exception as e:
        print(f"Approve review error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return redirect("/seller/review-requests")


@seller_bp.route("/seller/reject-review/<int:order_id>", methods=['POST'])
def reject_review(order_id):
    if not session.get("seller_id"):
        return redirect("/seller/login")
    
    seller_id = session.get("seller_id")
    rejection_reason = request.form.get('rejection_reason', '')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM orders WHERE id=%s AND seller_id=%s AND status='review_submitted'", (order_id, seller_id))
        if cur.fetchone():
            cur.execute("""
                UPDATE orders 
                SET status = 'rejected', 
                    rejection_reason = %s, 
                    rejected_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (rejection_reason, order_id))
            conn.commit()
    except Exception as e:
        print(f"Reject review error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
    return redirect("/seller/review-requests")


@seller_bp.route("/seller/payment-history")
def seller_payment_history():
    if not session.get("seller_id"):
        return redirect("/seller/login")
    
    seller_id = session.get("seller_id")
    seller_name = session.get("seller_name")
    
    conn = db()
    cur = conn.cursor()
    batches = []
    
    try:
        cur.execute("""
            SELECT pb.id, pb.batch_id, pb.total_orders, pb.total_refund_amount, 
                   pb.status, pb.created_at, pb.processed_at
            FROM payment_batches pb
            WHERE pb.seller_id = %s
            ORDER BY pb.created_at DESC
        """, (seller_id,))
        
        rows = cur.fetchall()
        for r in rows:
            # Get items for this batch - directly from orders table
            cur.execute("""
                SELECT o.id, o.order_id, o.product_name, o.refund_amount, o.status
                FROM orders o
                WHERE o.batch_id = %s
            """, (r[1],))
            item_rows = cur.fetchall()
            
            batch_item_list = []
            for item in item_rows:
                batch_item_list.append({
                    "order_id": item[0],
                    "order_number": item[1],
                    "product_name": item[2],
                    "refund_amount": float(item[3]) if item[3] else 0,
                    "status": item[4] if item[4] else 'pending'
                })
            
            batches.append({
                "id": r[0],
                "batch_id": r[1],
                "total_orders": r[2],
                "total_refund_amount": float(r[3]) if r[3] else 0,
                "status": r[4],
                "created_at": r[5].strftime('%d-%m-%Y %H:%M') if r[5] else '-',
                "processed_at": r[6].strftime('%d-%m-%Y %H:%M') if r[6] else '-',
                "batch_items": batch_item_list
            })
            
    except Exception as e:
        print(f"Payment history error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()
    
    return render_template("Seller/seller_payment_history.html", batches=batches, seller_name=seller_name)


@seller_bp.route("/seller/product/ordered-count/<int:product_id>")
def get_product_ordered_count(product_id):
    if not session.get("seller_id"):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    
    seller_id = session.get("seller_id")
    
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*) FROM orders 
            WHERE product_id = %s AND seller_id = %s
        """, (product_id, seller_id))
        ordered_count = cur.fetchone()[0] or 0
        
        return jsonify({"success": True, "ordered_count": ordered_count})
    except Exception as e:
        print(f"Error getting ordered count: {e}")
        return jsonify({"success": False, "error": str(e)})
    finally:
        cur.close()
        conn.close()


@seller_bp.route("/seller/product/update-limit", methods=["POST"])
def update_product_limit():
    if not session.get("seller_id"):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    
    data = request.get_json()
    product_id = data.get("product_id")
    new_limit = data.get("new_limit")
    seller_id = session.get("seller_id")
    
    if not product_id or not new_limit:
        return jsonify({"success": False, "error": "Product ID and new limit required"})
    
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM products WHERE id=%s AND seller_id=%s", (product_id, seller_id))
        if not cur.fetchone():
            return jsonify({"success": False, "error": "Product not found"})
        
        cur.execute("UPDATE products SET order_limit = %s WHERE id = %s", (new_limit, product_id))
        conn.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error updating limit: {e}")
        conn.rollback()
        return jsonify({"success": False, "error": str(e)})
    finally:
        cur.close()
        conn.close()
