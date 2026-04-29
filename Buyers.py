from flask import Blueprint, render_template, request, redirect, session, jsonify
from db import db
from authlib.integrations.flask_client import OAuth
import cloudinary
import cloudinary.uploader
from email_utils import send_email, send_welcome_email, send_otp_email
from datetime import datetime
import pytz
import random
import string

buyer_bp = Blueprint('buyer', __name__)
oauth = OAuth()

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')

# Store OTP temporarily
otp_storage = {}

def get_ist_now():
    return datetime.now(IST)

def format_ist_datetime(dt):
    if dt is None:
        return '-'
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    return dt.astimezone(IST).strftime('%d-%m-%Y %H:%M:%S')

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

cloudinary.config(
    cloud_name="dt6rrmzxw",
    api_key="989313237337689",
    api_secret="2AqUHd82DY4T5q0CPzIHwBi0b6I",
    secure=True
)

google = oauth.register(
    name='google',
    client_id="570802750817-96l8fun1b48lo3bh57al6git8cgergoq.apps.googleusercontent.com",
    client_secret="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",
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


@buyer_bp.route('/buyer/auth', methods=['GET', 'POST'])
def buyer_auth():
    if session.get('buyer_id'):
        return redirect('/buyer/dashboard')
    
    msg = ""
    show_otp_field = False
    temp_email = ""
    error = False
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == "login":
            email = request.form.get('email')
            password = request.form.get('password')
             
            conn = db()
            cur = conn.cursor()
            try:
                cur.execute("SELECT id, name, mobile FROM buyers WHERE email=%s AND password=%s", (email, password))
                user = cur.fetchone()
                if user:
                    session['buyer_id'] = user[0]
                    session['buyer_name'] = user[1]
                    session['buyer_email'] = email
                    session.permanent = True
                    
                    if not user[2] or user[2] == '':
                        return redirect('/buyer/complete-profile')
                    
                    return redirect('/buyer/dashboard')
                else:
                    msg = "Invalid credentials"
                    error = True
            except Exception as e:
                print(f"Login error: {e}")
                msg = "Something went wrong"
                error = True
            finally:
                cur.close()
                conn.close()
            
            return render_template('Buyer/buyer_auth.html', msg=msg, error=error, show_otp_field=False, temp_email="")
        
        elif action == "register":
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            upi = request.form.get('upi_id')
            number = request.form.get('number')
            
            conn = db()
            cur = conn.cursor()
            try:
                # Check if email already exists and verified
                cur.execute("SELECT id, is_email_verified FROM buyers WHERE email=%s", (email,))
                existing = cur.fetchone()
                
                if existing and existing[1]:
                    # Email already verified - return error as JSON for AJAX
                    return jsonify({
                        "success": False, 
                        "error": "email_exists",
                        "message": "Email already registered. Please login."
                    })
                
                # If email exists but not verified, delete it
                if existing and not existing[1]:
                    cur.execute("DELETE FROM buyers WHERE email=%s", (email,))
                    conn.commit()
                
                # Store registration data temporarily
                otp = generate_otp()
                otp_storage[email] = {
                    'otp': otp,
                    'expires_at': datetime.now(IST).timestamp() + 300,
                    'data': {
                        'name': name,
                        'email': email,
                        'password': password,
                        'upi': upi,
                        'number': number
                    }
                }
                
                # Send OTP email
                send_otp_email(email, name, otp)
                
                # Return success with OTP data
                return jsonify({
                    "success": True,
                    "email": email,
                    "message": "OTP sent successfully"
                })
                
            except Exception as e:
                print(f"Register error: {e}")
                conn.rollback()
                return jsonify({"success": False, "error": "server_error", "message": "Something went wrong"})
            finally:
                cur.close()
                conn.close()
        
        elif action == "verify_otp":
            email = request.form.get('email')
            entered_otp = request.form.get('otp')
            
            if not email or not entered_otp:
                return jsonify({"success": False, "message": "Please enter OTP"})
            
            if email not in otp_storage:
                return jsonify({"success": False, "message": "OTP expired or not found. Please register again."})
            
            stored_data = otp_storage[email]
            current_time = datetime.now(IST).timestamp()
            
            if current_time > stored_data['expires_at']:
                del otp_storage[email]
                return jsonify({"success": False, "message": "OTP expired. Please register again."})
            
            if entered_otp == stored_data['otp']:
                user_data = stored_data['data']
                conn = db()
                cur = conn.cursor()
                try:
                    cur.execute("""
                        INSERT INTO buyers (name, email, password, upi_id, mobile, is_email_verified, verified_at) 
                        VALUES (%s, %s, %s, %s, %s, true, %s)
                    """, (user_data['name'], user_data['email'], user_data['password'], 
                          user_data['upi'], user_data['number'], get_ist_now()))
                    conn.commit()
                    
                    cur.execute("SELECT id, name, mobile FROM buyers WHERE email=%s", (user_data['email'],))
                    user = cur.fetchone()
                    
                    session['buyer_id'] = user[0]
                    session['buyer_name'] = user[1]
                    session['buyer_email'] = user_data['email']
                    session.permanent = True
                    
                    if email in otp_storage:
                        del otp_storage[email]
                    
                    send_welcome_email(user_data['email'], user[1])
                    
                    return jsonify({"success": True, "redirect": "/buyer/dashboard"})
                    
                except Exception as e:
                    print(f"OTP verification error: {e}")
                    conn.rollback()
                    return jsonify({"success": False, "message": "Something went wrong"})
                finally:
                    cur.close()
                    conn.close()
            else:
                return jsonify({"success": False, "message": "Invalid OTP. Please try again."})
    
    return render_template('Buyer/buyer_auth.html', msg=msg, error=error, show_otp_field=show_otp_field, temp_email=temp_email)


@buyer_bp.route('/buyer/resend-otp', methods=['POST'])
def resend_otp():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"success": False, "message": "Email required"}), 400
    
    if email not in otp_storage:
        return jsonify({"success": False, "message": "Session expired. Please register again."}), 400
    
    new_otp = generate_otp()
    user_data = otp_storage[email]['data']
    
    otp_storage[email] = {
        'otp': new_otp,
        'expires_at': datetime.now(IST).timestamp() + 300,
        'data': user_data
    }
    
    send_otp_email(email, user_data['name'], new_otp)
    
    return jsonify({"success": True, "message": "OTP resent successfully"})


@buyer_bp.route('/buyer/google/login')
def google_login():
    base_url = request.url_root.rstrip('/')
    if base_url.startswith('http://'):
        base_url = base_url.replace('http://', 'https://', 1)
    
    redirect_uri = base_url + '/buyer/google/callback'
    print(f"🔐 Redirect URI: {redirect_uri}")
    
    return google.authorize_redirect(redirect_uri)


@buyer_bp.route('/buyer/google/callback')
def google_callback():
    try:
        token = google.authorize_access_token()
    except Exception as e:
        print(f"OAuth error: {e}")
        return redirect('/buyer/auth?msg=Google+login+failed+please+try+again')
    
    user_info = token['userinfo']
    email = user_info['email']
    name = user_info['name']
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id, mobile, upi_id, password, name, is_email_verified FROM buyers WHERE email=%s", (email,))
        user = cur.fetchone()
        
        if user:
            session['buyer_id'] = user[0]
            session['buyer_name'] = user[4]
            session['buyer_email'] = email
            
            mobile_exists = user[1] and user[1] != ''
            upi_exists = user[2] and user[2] != ''
            password_exists = user[3] and user[3] != ''
            
            session.permanent = True
            
            if not mobile_exists or not upi_exists or not password_exists:
                return redirect('/buyer/complete-profile')
        else:
            cur.execute("""
                INSERT INTO buyers (name, email, upi_id, password, mobile, is_email_verified, verified_at) 
                VALUES (%s, %s, %s, %s, %s, true, %s)
            """, (name, email, "", "", "", get_ist_now()))
            conn.commit()
            
            cur.execute("SELECT id FROM buyers WHERE email=%s", (email,))
            session['buyer_id'] = cur.fetchone()[0]
            session['buyer_name'] = name
            session['buyer_email'] = email
            session.permanent = True
            send_welcome_email(email, name)
            return redirect('/buyer/complete-profile')
        
    except Exception as e:
        print(f"Google callback error: {e}")
    finally:
        cur.close()
        conn.close()
    
    return redirect('/buyer/dashboard')


# ============ REST OF THE FUNCTIONS (complete-profile, dashboard, etc.) ============
# [Keep all existing functions from your original Buyers.py here]

# ============ REST OF THE FUNCTIONS ============
@buyer_bp.route('/buyer/complete-profile', methods=['GET', 'POST'])
def complete_profile():
    if not session.get('buyer_id'):
        return redirect('/buyer/auth')
    
    buyer_id = session.get('buyer_id')
    msg = ""
    current_name = ""
    current_mobile = ""
    current_upi = ""
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT name, mobile, upi_id, password FROM buyers WHERE id = %s", (buyer_id,))
        buyer = cur.fetchone()
        
        if buyer:
            current_name = buyer[0] or ''
            current_mobile = buyer[1] or ''
            current_upi = buyer[2] or ''
            mobile_exists = buyer[1] and buyer[1] != ''
            upi_exists = buyer[2] and buyer[2] != ''
            password_exists = buyer[3] and buyer[3] != ''
            
            if mobile_exists and upi_exists and password_exists:
                return redirect('/buyer/dashboard')
        
        if request.method == 'POST':
            name = request.form.get('name')
            mobile = request.form.get('mobile')
            upi_id = request.form.get('upi_id')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not name or not mobile or not upi_id or not password:
                msg = "Please fill all fields"
            elif not mobile.isdigit() or len(mobile) != 10:
                msg = "Please enter a valid 10-digit mobile number"
            elif '@' not in upi_id:
                msg = "Please enter a valid UPI ID (e.g., name@okhdfcbank)"
            elif len(password) < 6:
                msg = "Password must be at least 6 characters"
            elif password != confirm_password:
                msg = "Passwords do not match"
            else:
                cur.execute("""
                    UPDATE buyers 
                    SET name = %s, mobile = %s, upi_id = %s, password = %s 
                    WHERE id = %s
                """, (name, mobile, upi_id, password, buyer_id))
                conn.commit()
                session['buyer_name'] = name
                send_welcome_email(session.get('buyer_email'), name)
                session.permanent = True
                return redirect('/buyer/dashboard')
        
    except Exception as e:
        print(f"Complete profile error: {e}")
        msg = "Something went wrong"
    finally:
        cur.close()
        conn.close()
    
    return render_template('Buyer/buyer_complete_profile.html', 
                          msg=msg, 
                          current_name=current_name,
                          current_mobile=current_mobile,
                          current_upi=current_upi)


@buyer_bp.route('/buyer/dashboard')
def buyer_dashboard():
    if not session.get('buyer_id'):
        return redirect('/buyer/auth')
    
    buyer_id = session.get('buyer_id')
    buyer_name = session.get('buyer_name')
    conn = db()
    cur = conn.cursor()
    products = []
    
    try:
        cur.execute("""
            SELECT p.id, p.name, p.brand, p.refund, p.link, p.order_limit,
                   COALESCE((SELECT COUNT(*) FROM orders o WHERE o.product_id = p.id AND o.buyer_id = %s), 0) as buyer_ordered,
                   COALESCE((SELECT COUNT(*) FROM orders o WHERE o.product_id = p.id), 0) as total_ordered
            FROM products p
            WHERE p.seller_id IN (SELECT id FROM sellers WHERE status = 'approved')
            ORDER BY p.id DESC
        """, (buyer_id,))
        
        rows = cur.fetchall()
        for r in rows:
            total_ordered = r[7] if len(r) > 7 else 0
            order_limit = r[5]
            
            if total_ordered < order_limit:
                products.append({
                    "id": r[0], "name": r[1], "brand": r[2], "refund": r[3], "link": r[4],
                    "order_limit": order_limit, "already_ordered": (r[6] if len(r) > 6 else 0) > 0,
                    "slots_left": order_limit - total_ordered
                })
    except Exception as e:
        print(f"Buyer dashboard error: {e}")
    finally:
        cur.close()
        conn.close()
    
    return render_template("Buyer/buyer_dashboard.html", products=products, buyer_name=buyer_name)


@buyer_bp.route('/buyer/place-order/<int:product_id>', methods=['GET', 'POST'])
def place_order(product_id):
    if not session.get('buyer_id'):
        return redirect('/buyer/auth')
    
    buyer_id = session.get('buyer_id')
    msg = ""
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT p.id, p.name, p.refund, p.order_limit, p.seller_id,
                   COALESCE((SELECT COUNT(*) FROM orders WHERE product_id = p.id), 0) as total_ordered, p.link
            FROM products p WHERE p.id = %s
        """, (product_id,))
        product = cur.fetchone()
        
        if not product:
            return redirect('/buyer/dashboard')
        
        product_id_db = product[0]
        product_name = product[1]
        refund_amount = product[2]
        order_limit = product[3]
        seller_id = product[4]
        total_ordered = product[5]
        
        if total_ordered >= order_limit:
            msg = "This product's order limit has been reached."
            return render_template("Buyer/buyer_place_order.html", product=product, msg=msg, error=True)
        
        cur.execute("SELECT id FROM orders WHERE buyer_id=%s AND product_id=%s", (buyer_id, product_id_db))
        if cur.fetchone():
            msg = "You have already placed an order for this product."
            return render_template("Buyer/buyer_place_order.html", product=product, msg=msg, error=True)
        
        if request.method == 'POST':
            amazon_order_id = request.form.get('amazon_order_id')
            order_amount = request.form.get('order_amount')
            
            order_screenshot_url = None
            if 'order_screenshot' in request.files:
                file = request.files['order_screenshot']
                if file and file.filename:
                    upload_result = cloudinary.uploader.upload(file, folder=f"heavydeals/orders/{buyer_id}")
                    order_screenshot_url = upload_result.get('secure_url')
            
            if not all([amazon_order_id, order_amount, order_screenshot_url]):
                msg = "Please fill all fields and upload screenshot"
            else:
                ist_now = get_ist_now()
                cur.execute("""
                    INSERT INTO orders (order_id, buyer_id, seller_id, product_id, product_name, 
                                       order_amount, refund_amount, status, order_screenshot, order_placed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', %s, %s)
                """, (amazon_order_id, buyer_id, seller_id, product_id_db, product_name, 
                      order_amount, refund_amount, order_screenshot_url, ist_now))
                conn.commit()

                ist_time_str = format_ist_datetime(ist_now)
                send_email(
                    to_email=session.get('buyer_email'),
                    subject=f"Order Confirmation - {amazon_order_id}",
                    message=f"Your order has been placed successfully!\n\nOrder ID: {amazon_order_id}\nProduct: {product_name}\nAmount: ₹{order_amount}\nReward: ₹{refund_amount/2}\nOrder Date (IST): {ist_time_str}\nOrder ScreenShot: {order_screenshot_url}"
                )

                send_email(
                    to_email="bhalanijaynil@gmail.com",
                    subject=f"New Order Received - {amazon_order_id}",
                    message=f"A new order has been placed.\n\nOrder ID: {amazon_order_id}\n\nBuyer: {session.get('buyer_name')}\nBuyer Email: {session.get('buyer_email')}\nProduct: {product_name}\nAmount: ₹{order_amount}\nReward: ₹{refund_amount/2}\nOrder Date (IST): {ist_time_str}\nOrder ScreenShot: {order_screenshot_url}"
                )
                return redirect('/buyer/dashboard')
        
    except Exception as e:
        print(f"Place order error: {e}")
        msg = "Something went wrong"
    finally:
        cur.close()
        conn.close()
    
    product_dict = {'id': product[0], 'name': product[1], 'refund': product[2], 'order_limit': product[3], 'link': product[6]}
    return render_template("Buyer/buyer_place_order.html", product=product_dict, msg=msg, buyer_name=session.get('buyer_name'))


@buyer_bp.route('/buyer/my-orders')
def buyer_my_orders():
    if not session.get('buyer_id'):
        return redirect('/buyer/auth')
    
    buyer_id = session.get('buyer_id')
    buyer_name = session.get('buyer_name', 'Customer')
    
    conn = db()
    cur = conn.cursor()
    orders = []
    
    try:
        if buyer_name == 'Customer':
            cur.execute("SELECT name, email FROM buyers WHERE id = %s", (buyer_id,))
            result = cur.fetchone()
            if result:
                buyer_name = result[0]
                buyer_email = result[1]
                session['buyer_name'] = buyer_name
                session['buyer_email'] = buyer_email
        
        cur.execute("""
            SELECT id, order_id, product_name, order_amount, refund_amount, 
                   status, order_placed_at, order_screenshot, review_screenshot, 
                   review_link, delivered_screenshot, rejection_reason, 
                   paid_at, review_submitted_at
            FROM orders WHERE buyer_id = %s ORDER BY id DESC
        """, (buyer_id,))
        
        for r in cur.fetchall():
            orders.append({
                "id": r[0],
                "order_id": r[1],
                "product_name": r[2],
                "order_amount": r[3],
                "refund_amount": r[4],
                "status": r[5],
                "order_placed_at": format_ist_datetime(r[6]) if r[6] else '-',
                "order_screenshot": r[7],
                "review_screenshot": r[8],
                "review_link": r[9],
                "delivered_screenshot": r[10],
                "rejection_reason": r[11] if len(r) > 11 and r[11] else None,
                "paid_at": format_ist_datetime(r[12]) if len(r) > 12 and r[12] else '-',
                "review_submitted_at": format_ist_datetime(r[13]) if len(r) > 13 and r[13] else '-'
            })
    except Exception as e:
        print(f"My orders error: {e}")
    finally:
        cur.close()
        conn.close()
    
    return render_template("Buyer/buyer_my_orders.html", orders=orders, buyer_name=buyer_name)


@buyer_bp.route('/buyer/submit-review/<int:order_id>', methods=['GET', 'POST'])
def submit_review(order_id):
    if not session.get('buyer_id'):
        return redirect('/buyer/auth')
    
    buyer_id = session.get('buyer_id')
    msg = ""
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id, status, product_name, order_id FROM orders WHERE id=%s AND buyer_id=%s", (order_id, buyer_id))
        order = cur.fetchone()
        
        if not order:
            return redirect('/buyer/my-orders')
        
        if order[1] not in ['pending', 'review_submitted']:
            msg = "Review already submitted"
            order_dict = {'id': order[0], 'status': order[1], 'product_name': order[2], 'order_id': order[3]}
            return render_template("Buyer/buyer_submit_review.html", order=order_dict, msg=msg, error=True)
        
        if request.method == 'POST':
            review_link = request.form.get('review_link')
            
            delivered_screenshot_url = None
            if 'delivered_screenshot' in request.files:
                file = request.files['delivered_screenshot']
                if file and file.filename:
                    upload_result = cloudinary.uploader.upload(file, folder=f"heavydeals/delivered/{buyer_id}")
                    delivered_screenshot_url = upload_result.get('secure_url')
            
            review_screenshot_url = None
            if 'review_screenshot' in request.files:
                file = request.files['review_screenshot']
                if file and file.filename:
                    upload_result = cloudinary.uploader.upload(file, folder=f"heavydeals/reviews/{buyer_id}")
                    review_screenshot_url = upload_result.get('secure_url')
            
            if not all([review_link, delivered_screenshot_url, review_screenshot_url]):
                msg = "Please fill all fields and upload both screenshots"
            else:
                ist_now = get_ist_now()
                cur.execute("""
                    UPDATE orders SET delivered_screenshot = %s, review_screenshot = %s, review_link = %s,
                        status = 'review_submitted', review_submitted_at = %s WHERE id = %s
                """, (delivered_screenshot_url, review_screenshot_url, review_link, ist_now, order_id))
                conn.commit()

                cur.execute("SELECT product_name, order_amount, refund_amount, order_placed_at FROM orders WHERE id = %s", (order_id,))
                order_details = cur.fetchone()
                product_name = order_details[0]
                order_amount = order_details[1]
                refund_amount = order_details[2]
                order_placed_at = order_details[3]
                ist_time_str = format_ist_datetime(order_placed_at) 

                


                send_email(
                    to_email=session.get('buyer_email'),
                    subject=f"Order Review Confirmation - {order_id}",
                    message=f"Your order review has been submitted successfully!\n\nOrder ID: {order_id}\nProduct: {product_name}\nAmount: ₹{order_amount}\nReward: ₹{refund_amount/2}\nOrder Date (IST): {ist_time_str}\nDelivered Screenshot: {delivered_screenshot_url}\nReview Screenshot: {review_screenshot_url}\nReview Link: {review_link}"
                )
                return redirect('/buyer/my-orders')
        
    except Exception as e:
        print(f"Submit review error: {e}")
        msg = "Something went wrong"
    finally:
        cur.close()
        conn.close()
    
    order_dict = {'id': order[0], 'status': order[1], 'product_name': order[2], 'order_id': order[3]}
    return render_template("Buyer/buyer_submit_review.html", order=order_dict, msg=msg)


@buyer_bp.route('/buyer/profile')
def buyer_profile():
    if not session.get('buyer_id'):
        return redirect('/buyer/auth')
    
    buyer_id = session.get('buyer_id')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT name, email, upi_id, mobile
            FROM buyers 
            WHERE id = %s
        """, (buyer_id,))
        
        buyer = cur.fetchone()
        
        if not buyer:
            return redirect('/buyer/auth')
        
        buyer_name = buyer[0]
        buyer_email = buyer[1]
        buyer_upi = buyer[2]
        buyer_mobile = buyer[3] or ''
        
        session['buyer_name'] = buyer_name
        session['buyer_email'] = buyer_email
        
    except Exception as e:
        print(f"Profile error: {e}")
        buyer_name = session.get('buyer_name', 'Customer')
        buyer_email = ''
        buyer_upi = ''
        buyer_mobile = ''
    finally:
        cur.close()
        conn.close()
    
    return render_template('Buyer/buyer_profile.html', 
                          buyer_name=buyer_name,
                          buyer_email=buyer_email,
                          buyer_upi=buyer_upi,
                          buyer_mobile=buyer_mobile,
                          is_editing=False)


@buyer_bp.route('/buyer/profile/edit')
def buyer_profile_edit():
    if not session.get('buyer_id'):
        return redirect('/buyer/auth')
    
    buyer_id = session.get('buyer_id')
    
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT name, email, upi_id, mobile
            FROM buyers 
            WHERE id = %s
        """, (buyer_id,))
        
        buyer = cur.fetchone()
        
        if not buyer:
            return redirect('/buyer/auth')
        
        buyer_name = buyer[0]
        buyer_email = buyer[1]
        buyer_upi = buyer[2]
        buyer_mobile = buyer[3] or ''
        
    except Exception as e:
        print(f"Profile edit error: {e}")
        buyer_name = session.get('buyer_name', 'Customer')
        buyer_email = ''
        buyer_upi = ''
        buyer_mobile = ''
    finally:
        cur.close()
        conn.close()
    
    return render_template('Buyer/buyer_profile.html', 
                          buyer_name=buyer_name,
                          buyer_email=buyer_email,
                          buyer_upi=buyer_upi,
                          buyer_mobile=buyer_mobile,
                          is_editing=True)


def render_edit_profile_with_error(buyer_id, msg, error):
    conn = db()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT name, email, upi_id, mobile
            FROM buyers 
            WHERE id = %s
        """, (buyer_id,))
        
        buyer = cur.fetchone()
        buyer_name = buyer[0] if buyer else session.get('buyer_name', 'Customer')
        buyer_email = buyer[1] if buyer else ''
        buyer_upi = buyer[2] if buyer else ''
        buyer_mobile = buyer[3] if buyer else ''
        
    except Exception as e:
        buyer_name = session.get('buyer_name', 'Customer')
        buyer_email = ''
        buyer_upi = ''
        buyer_mobile = ''
    finally:
        cur.close()
        conn.close()
    
    return render_template('Buyer/buyer_profile.html', 
                          buyer_name=buyer_name,
                          buyer_email=buyer_email,
                          buyer_upi=buyer_upi,
                          buyer_mobile=buyer_mobile,
                          is_editing=True,
                          msg=msg,
                          error=error)


@buyer_bp.route('/buyer/profile/update', methods=['POST'])
def buyer_profile_update():
    if not session.get('buyer_id'):
        return redirect('/buyer/auth')
    
    buyer_id = session.get('buyer_id')
    
    name = request.form.get('name')
    email = request.form.get('email')
    mobile = request.form.get('mobile')
    upi_id = request.form.get('upi_id')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    msg = ""
    error = False
    
    if not name or not email:
        msg = "Name and email are required"
        error = True
        return render_edit_profile_with_error(buyer_id, msg, error)
    
    if mobile:
        if not mobile.isdigit() or len(mobile) != 10:
            msg = "Please enter a valid 10-digit mobile number"
            error = True
            return render_edit_profile_with_error(buyer_id, msg, error)
    
    if upi_id and '@' not in upi_id:
        msg = "Please enter a valid UPI ID (e.g., name@okhdfcbank)"
        error = True
        return render_edit_profile_with_error(buyer_id, msg, error)
    
    if password:
        if len(password) < 6:
            msg = "Password must be at least 6 characters"
            error = True
            return render_edit_profile_with_error(buyer_id, msg, error)
        if password != confirm_password:
            msg = "Passwords do not match"
            error = True
            return render_edit_profile_with_error(buyer_id, msg, error)
    
    conn = db()
    cur = conn.cursor()
    
    try:
        # Check if email already exists for another user
        cur.execute("SELECT id FROM buyers WHERE email = %s AND id != %s", (email, buyer_id))
        if cur.fetchone():
            msg = "Email already exists for another account"
            error = True
            return render_edit_profile_with_error(buyer_id, msg, error)
        
        # Update query
        if password:
            cur.execute("""
                UPDATE buyers 
                SET name = %s, email = %s, mobile = %s, upi_id = %s, password = %s
                WHERE id = %s
            """, (name, email, mobile, upi_id, password, buyer_id))
        else:
            cur.execute("""
                UPDATE buyers 
                SET name = %s, email = %s, mobile = %s, upi_id = %s
                WHERE id = %s
            """, (name, email, mobile, upi_id, buyer_id))
        
        conn.commit()
        
        # Update session
        session['buyer_name'] = name
        session['buyer_email'] = email
        
        msg = "Profile updated successfully!"
        
    except Exception as e:
        print(f"Profile update error: {e}")
        conn.rollback()
        msg = "Something went wrong"
        error = True
    finally:
        cur.close()
        conn.close()
    
    # Redirect with message
    return redirect('/buyer/profile?msg=' + msg + ('&error=1' if error else ''))
