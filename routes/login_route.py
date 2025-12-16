import re
from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
from routes.email_utils import send_otp_email
import random
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"
MAX_EMAIL_LEN = 254
MAX_PASSWORD_LEN = 128
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        # ✅ Remember Me (clear & explicit)
        remember_me = request.form.get("remember_me") == "on"
        session.permanent = remember_me

        # ---------------- BASIC VALIDATION ----------------
        if not email:
            flash("Email required.", "error")
            return render_template("login.html")

        if not password:
            flash("Password required.", "error")
            return render_template("login.html")

        if not re.match(EMAIL_REGEX, email):
            flash("Enter valid email.", "error")
            return render_template("login.html")

        if len(email) > MAX_EMAIL_LEN or len(password) > MAX_PASSWORD_LEN:
            flash("Input exceeds allowed length.", "error")
            return render_template("login.html")

        conn = get_connection()
        cur = conn.cursor()

        # ---------------- FETCH USER ----------------
        cur.execute("""
            SELECT u.id, u.email, u.password, r.name
            FROM users_master u
            LEFT JOIN roles_master r ON u.role_id = r.id
            WHERE u.email = %s
        """, (email,))

        row = cur.fetchone()

        if not row:
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        user_id, user_email, stored_hash, user_role = row

        if isinstance(stored_hash, (bytes, memoryview)):
            stored_hash = stored_hash.tobytes().decode()

        # ---------------- PASSWORD CHECK ----------------
        if not check_password_hash(stored_hash, password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        # ---------------- OTP GENERATION ----------------
        otp = random.randint(100000, 999999)

        session["pending_user_id"] = user_id
        session["pending_user_email"] = user_email
        session["pending_user_role"] = user_role.lower() if user_role else "student"
        session["login_otp"] = str(otp)
        session["otp_expires_at"] = (
            datetime.utcnow() + timedelta(minutes=5)
        ).isoformat()

        try:
            send_otp_email(user_email, otp)
            flash("OTP sent to your email.", "success")
            return redirect(url_for("verify_otp"))
        except Exception as e:
            # 🔐 Remember Me is still preserved
            print("EMAIL ERROR:", e)
            flash("Could not send OTP. Check email settings.", "error")
            return render_template("login.html")

    return render_template("login.html")
