from flask import Flask, render_template, session, redirect, request
from Seller import seller_bp
from Buyers import buyer_bp, oauth
from Admin import admin_bp
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "heavy-deals-secret-key-change-in-production"
app.permanent_session_lifetime = timedelta(days=3650)

# ✅ Force HTTPS Redirect for all HTTP requests
@app.before_request
def force_https():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

# ✅ Add Security Headers
@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Initialize OAuth with Flask app
oauth.init_app(app)

# Register Blueprints
app.register_blueprint(seller_bp)
app.register_blueprint(buyer_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def first():
    return render_template("First.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
