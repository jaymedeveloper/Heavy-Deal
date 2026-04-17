from flask import Flask, render_template, request, redirect, session, Response, Blueprint
from db import db

seller_bp = Blueprint('seller', __name__)


@seller_bp.before_request
def check_seller_login():
    if "seller_id" not in session:
        return redirect("/seller/login")


@seller_bp.route("/seller/login", methods=['GET', 'POST'])
def seller_login():
    msg=""
    if request.method=="POST":
        username = request.form["username"]
        password = request.form['password'] 

        conn=db()
        cur=conn.cursor()
        cur.execute("SELECT id,name FROM sellers WHERE username=%s and pass=%s",(username,password))
        data = cur.fetchone()
        cur.close()
        conn.close()

        if data:
            session["seller_id"]=data[0]
            session["seller_name"]=data[1]

            return redirect("/seller/dashboard")
        else:
            msg="Invalid Username or Password"

    return render_template("Seller/seller_login.html",msg = msg)

@seller_bp.route("/seller/dashboard")
def seller_dashboard():
    name=session.get("seller_name")
    return render_template(
        "Seller/seller_dashboard.html",
        seller_name = name,
        total_orders=10,
        approved_orders=5,
        pending_orders=5,
        total_amount=2500
    )

@seller_bp.route("/seller/products")
def seller_products():

    conn=db()
    cur=conn.cursor()
    cur.execute("SELECT name,brand,refund,order_limit,link FROM products WHERE seller_id=%s",(session.get('seller_id'),))
    products=cur.fetchall()
    cur.close()
    conn.close()

    return render_template(
        "Seller/seller_products.html",
        seller_name="Jayme",
        products=products
    )

@seller_bp.route("/seller/products/add", methods=["POST"])
def add_product():

    name = request.form["name"]
    link = request.form["link"]
    refund = request.form["refund"]
    brand = request.form["brand"]
    limit = request.form["limit"]

    # abhi print karo (baad me DB / Google Sheet)
    conn=db()
    cur=conn.cursor()
    cur.execute("INSERT INTO products (name,link,refund,brand,order_limit,seller_id) values(%s,%s,%s,%s,%s,%s)",(name,link,refund,brand,limit,session.get('seller_id')))
    conn.commit()
    cur.close()
    conn.close()
    print(name, link, refund, brand, limit)

    return redirect("/seller/products")

@seller_bp.route("/seller/orders")
def seller_orders():

    seller_id = session.get("seller_id")

    # DB se orders fetch karo

    conn=db()
    cur = conn.cursor()
    cur.execute("""
        SELECT product_name, order_id, buyer_name, status, screenshot
        FROM orders
        WHERE seller_id = %s
        ORDER BY id DESC
    """, (seller_id,))

    rows = cur.fetchall()

    # convert to dict (best practice)
    orders = []
    for r in rows:
        orders.append({
            "product": r[0],
            "order_id": r[1],
            "buyer": r[2],
            "status": r[3],
            "screenshot": r[4]
        })

    return render_template("seller_orders.html",
                           orders=orders,
                           seller_name=session.get("seller_name"))