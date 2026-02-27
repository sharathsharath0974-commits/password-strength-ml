from flask import Flask, render_template, request, redirect, session
from auth import init_db, create_user, verify_user
import joblib, os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

app = Flask(__name__)
app.secret_key = "super-secret-key"

# ---------------- SECURITY ----------------
# Rate limiting
limiter = Limiter(get_remote_address, app=app)

# Security headers (DO NOT force HTTPS on localhost)
Talisman(
    app,
    content_security_policy=None,
    force_https=False   # 🔴 IMPORTANT FIX
)

# ---------------- ML MODEL ----------------
model = joblib.load("password_model.pkl")

def password_strength(p):
    features = [[
        len(p),
        sum(c.isdigit() for c in p),
        sum(c.isupper() for c in p),
        sum(c.islower() for c in p),
        sum(not c.isalnum() for c in p)
    ]]
    return "Strong" if model.predict(features)[0] == 1 else "Weak"

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    message = ""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if verify_user(email, password):
            session["user"] = email
            return redirect("/dashboard")
        else:
            message = "Invalid email or password"

    return render_template("login.html", message=message)

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per minute")
def register():
    message = ""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if create_user(email, password):
            return redirect("/")
        else:
            message = "Email already registered"

    return render_template("register.html", message=message)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    result = ""
    if request.method == "POST":
        pwd = request.form.get("password")
        result = password_strength(pwd)

    return render_template("dashboard.html", user=session["user"], result=result)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# ---------------- START ----------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))