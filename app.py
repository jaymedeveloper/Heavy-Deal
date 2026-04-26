from flask import Flask, render_template, session, redirect
from Seller import seller_bp
from Buyers import buyer_bp, oauth
from Admin import admin_bp
from datetime import timedelta, datetime
import pytz

app = Flask(__name__)
app.secret_key = "heavy-deals-secret-key-change-in-production"
app.permanent_session_lifetime = timedelta(days=3650)

# ✅ IST Timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Get current time in IST"""
    return datetime.now(IST)

@app.template_filter('ist_time')
def ist_time_filter(timestamp):
    """Convert to IST for display"""
    if timestamp:
        if hasattr(timestamp, 'strftime'):
            if timestamp.tzinfo is None:
                timestamp = pytz.UTC.localize(timestamp)
            return timestamp.astimezone(IST).strftime('%d-%m-%Y %H:%M:%S')
        return str(timestamp)
    return '-'

@app.template_filter('ist_date')
def ist_date_filter(timestamp):
    """Convert to IST date only"""
    if timestamp:
        if hasattr(timestamp, 'strftime'):
            if timestamp.tzinfo is None:
                timestamp = pytz.UTC.localize(timestamp)
            return timestamp.astimezone(IST).strftime('%d-%m-%Y')
        return str(timestamp)
    return '-'

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
