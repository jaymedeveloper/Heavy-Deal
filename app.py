from flask import Flask, render_template, session, redirect
from Seller import seller_bp
from Buyers import buyer_bp, oauth
from Admin import admin_bp
from datetime import timedelta

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)