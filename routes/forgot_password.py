from flask import render_template, request, flash, redirect, url_for
from app import app
from db import get_connection
from routes.email_utils import send_password_reset_email
import secrets
from datetime import datetime, timedelta

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        conn = get_connection()
        cur = conn.cursor()

        # ✅ TC_LOGIN_024: Find user (non-enumerable)
        cur.execute("SELECT id FROM users_master WHERE email = %s", (email,))
        user = cur.fetchone()

        # Always show generic message (no enumeration)
        if user:
            user_id = user[0]
            
            # Generate reset token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Create password_reset_tokens table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT REFERENCES users_master(id) ON DELETE CASCADE,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Store token
            cur.execute("""
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user_id, token, expires_at))
            conn.commit()
            
            # ✅ TC_LOGIN_023: Send email with reset link
            try:
                reset_link = url_for('reset_password', token=token, _external=True)
                send_password_reset_email(email, reset_link)
            except Exception as e:
                print("Email error:", e)

        cur.close()
        conn.close()

        flash(
            "If the email is registered, a password reset link has been sent.",
            "success"
        )
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """✅ TC_LOGIN_025: Reset password with expired link check"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Validate token
    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id TEXT REFERENCES users_master(id) ON DELETE CASCADE,
            token VARCHAR(255) UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        SELECT user_id, expires_at FROM password_reset_tokens
        WHERE token = %s
    """, (token,))
    
    row = cur.fetchone()
    
    if not row:
        flash("Invalid reset link.", "error")
        cur.close()
        conn.close()
        return redirect(url_for("login"))
    
    user_id, expires_at = row
    
    if datetime.utcnow() > expires_at:
        flash("Link expired.", "error")
        cur.close()
        conn.close()
        return redirect(url_for("login"))
    
    if request.method == "POST":
        new_password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Validate
        if len(new_password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("reset_password.html", token=token)
        
        if new_password != confirm_password:
            flash("Passwords don't match.", "error")
            return render_template("reset_password.html", token=token)
        
        from werkzeug.security import generate_password_hash
        hashed = generate_password_hash(new_password, method="pbkdf2:sha256", salt_length=16)
        
        # Update password
        cur.execute("""
            UPDATE users_master SET password = %s WHERE id = %s
        """, (hashed, user_id))
        
        # Delete token
        cur.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Password reset successful! Please login with your new password.", "success")
        return redirect(url_for("login"))
    
    cur.close()
    conn.close()
    return render_template("reset_password.html", token=token)
