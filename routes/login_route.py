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
            SELECT u.user_id, u.email, u.password, u.failed_attempts,
                   u.lock_until, r.role_name
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.email = %s
        """, (email,))

        row = cur.fetchone()

        if not row:
            cur.close()
            conn.close()
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        user_id, user_email, stored_hash, failed_attempts, lock_until, user_role = row

        # ---------------- LOCKOUT CHECK ----------------
        if lock_until and datetime.utcnow() < lock_until:
            flash("Account locked. Try again later.", "error")
            cur.close()
            conn.close()
            return render_template("login.html")

        if isinstance(stored_hash, (bytes, memoryview)):
            stored_hash = stored_hash.tobytes().decode()

        # ---------------- PASSWORD CHECK ----------------
        if not check_password_hash(stored_hash, password):

            failed_attempts += 1
            lock_time = None

            if failed_attempts >= MAX_FAILED_ATTEMPTS:
                lock_time = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)

            cur.execute("""
                UPDATE users
                SET failed_attempts = %s,
                    lock_until = %s
                WHERE user_id = %s
            """, (failed_attempts, lock_time, user_id))

            conn.commit()
            cur.close()
            conn.close()

            flash("Invalid email or password.", "error")
            return render_template("login.html")

        # ---------------- RESET FAILED ATTEMPTS ----------------
        cur.execute("""
            UPDATE users
            SET failed_attempts = 0,
                lock_until = NULL
            WHERE user_id = %s
        """, (user_id,))
        conn.commit()

        # ---------------- OTP GENERATION ----------------
        otp = random.randint(100000, 999999)

        session["pending_user_id"] = user_id
        session["pending_user_email"] = user_email
        session["pending_user_role"] = user_role
        session["login_otp"] = str(otp)
        session["otp_expires_at"] = (
            datetime.utcnow() + timedelta(minutes=5)
        ).isoformat()

        cur.close()
        conn.close()

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
