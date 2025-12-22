import re
from flask import render_template, request, redirect, url_for, flash, session
from app import app, limiter
from db import get_connection
from routes.email_utils import send_otp_email
import random
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from email_validator import validate_email, EmailNotValidError

EMAIL_REGEX = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
MAX_EMAIL_LEN = 254
MAX_PASSWORD_LEN = 128
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # ✅ TC_LOGIN_041: Rate limiting
def login():
    if request.method == "POST":

        email_input = request.form.get("email", "")
        password_input = request.form.get("password", "")
        
        email = email_input.strip().lower()
        password = password_input.strip()

        # ✅ TC_LOGIN_020: Show feedback if spaces trimmed
        if email_input != email_input.strip():
            flash("Spaces in email were trimmed.", "info")
        if password_input != password_input.strip():
            flash("Spaces in password were trimmed.", "info")

        # ✅ Remember Me (clear & explicit)
        remember_me = request.form.get("remember_me") == "on"
        session.permanent = remember_me

        # ✅ TC_LOGIN_004, TC_LOGIN_005: BASIC VALIDATION
        if not email:
            flash("Email required.", "error")
            return render_template("login.html")

        if not password:
            flash("Password required.", "error")
            return render_template("login.html")

        # ✅ TC_LOGIN_009, TC_LOGIN_010: Input length validation with feedback
        if len(email) > MAX_EMAIL_LEN:
            flash(f"Email exceeds maximum length of {MAX_EMAIL_LEN} characters.", "error")
            return render_template("login.html")
        
        if len(password) > MAX_PASSWORD_LEN:
            flash(f"Password exceeds maximum length of {MAX_PASSWORD_LEN} characters.", "error")
            return render_template("login.html")

        # ✅ TC_LOGIN_006, TC_LOGIN_050: Enhanced email validation (regex + international)
        if not re.match(EMAIL_REGEX, email):
            # Try email-validator for international emails
            try:
                valid_email = validate_email(email)
                email = valid_email.email
            except EmailNotValidError:
                flash("Enter valid email.", "error")
                return render_template("login.html")

        conn = get_connection()
        cur = conn.cursor()

        # ✅ TC_LOGIN_016: Check if account is locked
        cur.execute("""
            SELECT locked_until FROM users_master WHERE email = %s
        """, (email,))
        
        lock_check = cur.fetchone()
        if lock_check and lock_check[0] and datetime.utcnow() < lock_check[0]:
            minutes_left = int((lock_check[0] - datetime.utcnow()).total_seconds() / 60)
            flash(f"Account locked. Try again in {minutes_left} minutes.", "error")
            cur.close()
            conn.close()
            return render_template("login.html")

        # ✅ TC_LOGIN_001, TC_LOGIN_003: FETCH USER
        cur.execute("""
            SELECT u.id, u.email, u.password, r.name, u.failed_login_attempts
            FROM users_master u
            LEFT JOIN roles_master r ON u.role_id = r.id
            WHERE u.email = %s
        """, (email,))

        row = cur.fetchone()

        if not row:
            flash("Invalid email or password.", "error")
            cur.close()
            conn.close()
            return render_template("login.html")

        user_id, user_email, stored_hash, user_role, failed_attempts = row

        if isinstance(stored_hash, (bytes, memoryview)):
            stored_hash = stored_hash.tobytes().decode()

        # ✅ TC_LOGIN_002, TC_LOGIN_008: PASSWORD CHECK
        if not check_password_hash(stored_hash, password):
            # ❌ TC_LOGIN_016: Increment failed attempts
            cur.execute("""
                UPDATE users_master
                SET failed_login_attempts = failed_login_attempts + 1
                WHERE email = %s
            """, (email,))
            
            new_attempts = (failed_attempts or 0) + 1
            
            if new_attempts >= MAX_FAILED_ATTEMPTS:
                # Lock the account
                cur.execute("""
                    UPDATE users_master
                    SET locked_until = %s
                    WHERE email = %s
                """, (
                    datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES),
                    email
                ))
                flash(f"Account locked for {LOCKOUT_MINUTES} minutes due to multiple failed attempts.", "error")
            else:
                remaining = MAX_FAILED_ATTEMPTS - new_attempts
                flash(f"Invalid email or password. ({remaining} attempts remaining)", "error")
            
            conn.commit()
            cur.close()
            conn.close()
            return render_template("login.html")

        # ✅ SUCCESS - Reset failed attempts
        cur.execute("""
            UPDATE users_master
            SET failed_login_attempts = 0, locked_until = NULL
            WHERE email = %s
        """, (email,))
        conn.commit()

        # ✅ TC_LOGIN_044: OTP GENERATION (MFA)
        otp = random.randint(100000, 999999)

        session["pending_user_id"] = user_id
        session["pending_user_email"] = user_email
        session["pending_user_role"] = user_role.lower() if user_role else "student"
        session["login_otp"] = str(otp)
        session["otp_expires_at"] = (
            datetime.utcnow() + timedelta(minutes=5)
        ).isoformat()
        # ✅ TC_LOGIN_045: Set initial OTP resend cooldown
        session["otp_resend_at"] = (
            datetime.utcnow() + timedelta(seconds=60)
        ).isoformat()

        try:
            send_otp_email(user_email, otp)
            flash("OTP sent to your email.", "success")
            cur.close()
            conn.close()
            return redirect(url_for("verify_otp"))
        except Exception as e:
            print("EMAIL ERROR:", e)
            flash("Could not send OTP. Check email settings.", "error")
            cur.close()
            conn.close()
            return render_template("login.html")

    return render_template("login.html")
