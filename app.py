from flask import Flask, render_template, session, redirect
from Seller import seller_bp
from Buyers import buyer_bp, oauth
from Admin import admin_bp
from datetime import timedelta
import yagmail

app = Flask(__name__)
app.secret_key = "heavy-deals-secret-key-change-in-production"
app.permanent_session_lifetime = timedelta(days=3650)

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

# ✅ Simple Email Test Route
@app.route("/send-test-email")
def send_test_email():
    try:
        # Gmail credentials (replace with your app password)
        sender_email = "heavydeals567@gmail.com"
        sender_password = "xqsj qywl oaqh xajc"  # 🔴 Put your 16-char app password here
        
        receiver_email = "bhalanijaynil@gmail.com"
        subject = "Test Email from HeavyDeals"
        content = "Hii test pass"
        
        # Send email
        yag = yagmail.SMTP(sender_email, sender_password)
        yag.send(to=receiver_email, subject=subject, contents=content)
        
        return "✅ Email sent successfully to bhalanijaynil@gmail.com!"
        
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
