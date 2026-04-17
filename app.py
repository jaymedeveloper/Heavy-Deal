from flask import Flask, render_template, request, redirect, session, Response
from Seller import seller_bp
import gspread



app = Flask(__name__)
app.secret_key = "heavy-deals"
app.register_blueprint(seller_bp)

@app.route("/")
def first():
    return render_template("First.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)





