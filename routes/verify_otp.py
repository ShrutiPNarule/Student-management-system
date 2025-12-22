from flask import render_template, request, redirect, url_for, flash, session
from app import app
from datetime import datetime
import secrets
from db import get_connection


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    if "pending_user_email" not in session:
        flash("Session expired. Please login again.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":

        entered_otp = request.form.get("otp", "").strip()
        real_otp = session.get("login_otp")
        expires_at = session.get("otp_expires_at")

        if not entered_otp or not entered_otp.isdigit() or len(entered_otp) != 6:
            flash("Invalid OTP.", "error")
            return render_template("verify_otp.html")

        if not real_otp or not expires_at:
            flash("OTP expired. Please login again.", "error")
            return redirect(url_for("login"))

        if datetime.utcnow() > datetime.fromisoformat(expires_at):
            flash("OTP expired. Please login again.", "error")
            return redirect(url_for("login"))

        if entered_otp != real_otp:
            flash("Invalid OTP.", "error")
            return render_template("verify_otp.html")

        remember_me = session.permanent

        user_email = session["pending_user_email"]
        user_role = session["pending_user_role"]
        user_id = session.get("pending_user_id")

        session.clear()
        session.permanent = remember_me

        session["user_email"] = user_email
        session["role"] = user_role
        session["user_id"] = user_id

        # ✅ TC_LOGIN_014: Create persistent token if Remember Me checked
        if remember_me:
            conn = get_connection()
            cur = conn.cursor()
            
            token = secrets.token_urlsafe(32)
            from datetime import timedelta
            expires_at = datetime.utcnow() + timedelta(days=30)
            
            # Create persistent_tokens table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS persistent_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT REFERENCES users_master(id) ON DELETE CASCADE,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("""
                INSERT INTO persistent_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user_id, token, expires_at))
            conn.commit()
            cur.close()
            conn.close()
            
            # Set persistent cookie
            response = redirect(url_for("index"))
            response.set_cookie(
                'remember_token',
                token,
                max_age=30*24*3600,  # 30 days
                secure=False,  # Set to True in production
                httponly=True,
                samesite='Lax'
            )
            flash("Login successful!", "success")
            return response

        flash("Login successful!", "success")

        # ✅ TC_LOGIN_027: Redirect to previous page after login
        next_url = session.pop("next_url", None)
        return redirect(next_url or url_for("index"))

    return render_template("verify_otp.html")
