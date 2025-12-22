# LOGIN TEST CASES - ACTION PLAN & FIXES

## Quick Start Guide

This document provides step-by-step instructions to fix failing test cases.

---

## 🎯 CRITICAL PRIORITY (Fix First)

### Fix 1: Enable Rate Limiting (TC_LOGIN_041)
**Time**: 15 minutes  
**Difficulty**: Easy

#### Step 1: Update requirements.txt
```bash
# Add this line to requirements.txt
flask-limiter==3.5.0
```

#### Step 2: Install the package
```bash
pip install flask-limiter
```

#### Step 3: Modify login_route.py
```python
# At the top of login_route.py, add import
from app import app, limiter

# Change the login route decorator
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # ← ADD THIS LINE
def login():
    # ... rest of code ...
```

#### Step 4: Verify in app.py
Check that this code exists (it should):
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

---

### Fix 2: Account Lockout (TC_LOGIN_016, TC_LOGIN_017)
**Time**: 2-3 hours  
**Difficulty**: Medium

#### Step 1: Add database columns
```sql
-- Connect to PostgreSQL and run:
ALTER TABLE users_master ADD COLUMN IF NOT EXISTS failed_login_attempts INT DEFAULT 0;
ALTER TABLE users_master ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP;
```

#### Step 2: Update login_route.py
Replace the login function with this updated version:

```python
# At the top of login_route.py
from datetime import datetime, timedelta

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        remember_me = request.form.get("remember_me") == "on"
        session.permanent = remember_me

        # ✅ BASIC VALIDATION
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

        # ✅ CHECK IF ACCOUNT IS LOCKED
        cur.execute("""
            SELECT locked_until FROM users_master WHERE email = %s
        """, (email,))
        
        row = cur.fetchone()
        if row and row[0] and datetime.utcnow() < row[0]:
            minutes_left = int((row[0] - datetime.utcnow()).total_seconds() / 60)
            flash(f"Account locked. Try again in {minutes_left} minutes.", "error")
            cur.close()
            conn.close()
            return render_template("login.html")

        # ✅ FETCH USER
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

        # ✅ PASSWORD CHECK
        if not check_password_hash(stored_hash, password):
            # ❌ Increment failed attempts
            cur.execute("""
                UPDATE users_master
                SET failed_login_attempts = failed_login_attempts + 1
                WHERE email = %s
            """, (email,))
            
            # Check if limit exceeded
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
                conn.commit()
                flash(f"Account locked for {LOCKOUT_MINUTES} minutes due to multiple failed attempts.", "error")
            else:
                flash("Invalid email or password.", "error")
            
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

        # ✅ OTP GENERATION
        otp = random.randint(100000, 999999)

        session["pending_user_id"] = user_id
        session["pending_user_email"] = user_email
        session["pending_user_role"] = user_role.lower() if user_role else "student"
        session["login_otp"] = str(otp)
        session["otp_expires_at"] = (
            datetime.utcnow() + timedelta(minutes=5)
        ).isoformat()
        session["otp_resend_at"] = (  # ← FIX FOR TC_LOGIN_045
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
```

---

### Fix 3: Password Reset Email (TC_LOGIN_023)
**Time**: 3-4 hours  
**Difficulty**: Medium-High

#### Step 1: Create password_reset_tokens table
```sql
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id TEXT REFERENCES users_master(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_token ON password_reset_tokens(token);
```

#### Step 2: Update forgot_password.py
```python
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

        # Find user (non-enumerable)
        cur.execute("SELECT id FROM users_master WHERE email = %s", (email,))
        user = cur.fetchone()

        # Always show generic message
        if user:
            user_id = user[0]
            
            # Generate reset token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Store token
            cur.execute("""
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user_id, token, expires_at))
            conn.commit()
            
            # Send email
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
    conn = get_connection()
    cur = conn.cursor()
    
    # Validate token
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
        hashed = generate_password_hash(new_password, method="pbkdf2:sha256")
        
        # Update password
        cur.execute("""
            UPDATE users_master SET password = %s WHERE id = %s
        """, (hashed, user_id))
        
        # Delete token
        cur.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        flash("Password reset successful! Please login.", "success")
        return redirect(url_for("login"))
    
    cur.close()
    conn.close()
    return render_template("reset_password.html", token=token)
```

#### Step 3: Update email_utils.py
```python
# Add this function to email_utils.py

def send_password_reset_email(to_email, reset_link):
    subject = "Password Reset Request"
    body = f"""
    You requested a password reset. Click the link below to reset your password:
    
    {reset_link}
    
    This link expires in 24 hours.
    
    If you didn't request this, ignore this email.
    """
    
    message = f"Subject: {subject}\n\n{body}"
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, message)
```

#### Step 4: Create reset_password.html template
```html
{% extends "base.html" %}
{% block content %}

<div class="auth-wrapper">
  <div class="auth-card">
    <h2 class="auth-title">Reset Password</h2>
    
    <form method="post" class="auth-form">
      <div class="auth-field">
        <label for="password">New Password</label>
        <input
          type="password"
          id="password"
          name="password"
          required
          minlength="8"
          placeholder="Enter new password"
        >
      </div>
      
      <div class="auth-field">
        <label for="confirm_password">Confirm Password</label>
        <input
          type="password"
          id="confirm_password"
          name="confirm_password"
          required
          minlength="8"
          placeholder="Confirm new password"
        >
      </div>
      
      <button type="submit" class="btn btn-primary auth-btn">
        Reset Password
      </button>
    </form>
  </div>
</div>

{% endblock %}
```

---

## 🟡 HIGH PRIORITY (Fix Next)

### Fix 4: HTTPS Enforcement (TC_LOGIN_038)
**Time**: 30 minutes  
**Difficulty**: Easy

#### Option A: Test in Production Mode
```bash
# Don't use debug mode for testing
export FLASK_ENV=production
python app.py
```

#### Option B: Fix the condition
```python
# In app.py, modify enforce_https():
@app.before_request
def enforce_https():
    # Get environment variable
    env = os.getenv('ENVIRONMENT', 'development')
    
    # Enforce HTTPS in production or if explicitly set
    if not request.is_secure and env == 'production':
        return redirect(request.url.replace("http://", "https://"), code=301)
```

---

### Fix 5: Remember Me Persistence (TC_LOGIN_014)
**Time**: 2 hours  
**Difficulty**: Medium

#### Step 1: Create persistent_tokens table
```sql
CREATE TABLE IF NOT EXISTS persistent_tokens (
    id SERIAL PRIMARY KEY,
    user_id TEXT REFERENCES users_master(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_persistent_token ON persistent_tokens(token);
```

#### Step 2: Update login flow in verify_otp.py
```python
# Import at top
import secrets
from datetime import datetime, timedelta

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

        # ✅ CREATE PERSISTENT TOKEN IF REMEMBER ME
        if remember_me:
            conn = get_connection()
            cur = conn.cursor()
            
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=30)
            
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
                secure=True,
                httponly=True,
                samesite='Lax'
            )
            return response

        flash("Login successful!", "success")
        next_url = session.pop("next_url", None)
        return redirect(next_url or url_for("index"))

    return render_template("verify_otp.html")
```

#### Step 3: Add middleware to check persistent token on app startup
```python
# In app.py, add before_request handler
@app.before_request
def check_persistent_login():
    """Check if user has a persistent login token"""
    if 'user_email' not in session:
        token = request.cookies.get('remember_token')
        
        if token:
            conn = get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT u.id, u.email, r.name
                FROM persistent_tokens pt
                JOIN users_master u ON pt.user_id = u.id
                LEFT JOIN roles_master r ON u.role_id = r.id
                WHERE pt.token = %s AND pt.expires_at > NOW()
            """, (token,))
            
            row = cur.fetchone()
            
            if row:
                session['user_id'] = row[0]
                session['user_email'] = row[1]
                session['role'] = (row[2] or 'student').lower()
                session.permanent = True
            else:
                # Delete invalid/expired token
                cur.execute("DELETE FROM persistent_tokens WHERE token = %s", (token,))
            
            conn.commit()
            cur.close()
            conn.close()
```

---

## 🟠 MEDIUM PRIORITY (Fix Soon)

### Fix 6: Space Trimming Feedback (TC_LOGIN_020)
**Time**: 30 minutes

```python
# In login_route.py, after getting email and password:

email_input = request.form.get("email", "")
password_input = request.form.get("password", "")

email = email_input.strip().lower()
password = password_input.strip()

# Show feedback if spaces were trimmed
if email_input != email_input.strip():
    flash("Spaces in email were trimmed.", "info")
if password_input != password_input.strip():
    flash("Spaces in password were trimmed.", "info")
```

---

### Fix 7: Redirect to Previous Page (TC_LOGIN_027)
**Time**: 1-2 hours

```python
# Add middleware to app.py
@app.before_request
def capture_redirect_url():
    """Capture the URL requested before login"""
    if request.method == 'GET' and 'user_email' not in session:
        # List of protected endpoints
        protected = ['index', 'add', 'edit', 'delete', 'recycle_bin', 'logs', 'log_route']
        
        if request.endpoint in protected:
            session['next_url'] = request.url
```

---

## 🟢 LOW PRIORITY (Nice to Have)

### Fix 8: Accessibility - ARIA Labels (TC_LOGIN_034)
**Time**: 1 hour

```html
<!-- Update login.html password toggle: -->
<button
    type="button"
    id="password-toggle"
    onclick="togglePassword()"
    aria-label="Toggle password visibility"
    aria-pressed="false"
    style="background:none; border:none; cursor:pointer; position:absolute; right:10px; top:50%; transform:translateY(-50%);"
    title="Show / Hide Password"
>
    👁️
</button>

<!-- Update script to set aria-pressed: -->
<script>
function togglePassword() {
  const btn = document.getElementById("password-toggle");
  const pwd = document.getElementById("password");
  const isHidden = pwd.type === "password";
  pwd.type = isHidden ? "text" : "password";
  btn.setAttribute("aria-pressed", isHidden);
}
</script>

<!-- Add ARIA live region for messages: -->
<div id="flash-messages" role="alert" aria-live="polite" aria-atomic="true">
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
</div>
```

---

### Fix 9: Unicode Email Support (TC_LOGIN_050)
**Time**: 30 minutes

```bash
# Install email-validator
pip install email-validator
```

```python
# In login_route.py, update email validation:
from email_validator import validate_email, EmailNotValidError

# Replace the regex check with:
try:
    valid_email = validate_email(email)
    email = valid_email.email  # Normalized email
except EmailNotValidError:
    flash("Enter valid email.", "error")
    return render_template("login.html")
```

---

### Fix 10: Max Input Length Feedback (TC_LOGIN_009, TC_LOGIN_010)
**Time**: 1 hour

```html
<!-- Add to login.html: -->
<script>
document.getElementById("email").addEventListener("input", function() {
    if (this.value.length >= 250) {
        document.getElementById("email-length-warning").style.display = "block";
    } else {
        document.getElementById("email-length-warning").style.display = "none";
    }
});
</script>

<div id="email-length-warning" style="display:none; color:orange; font-size:0.9em;">
    ⚠️ Email length is close to maximum (254 characters)
</div>
```

---

## 📋 TESTING CHECKLIST

After each fix, test:
- [ ] Manual login test
- [ ] Test case passes with `python -m pytest test_login_suite.py`
- [ ] No new errors in Flask logs
- [ ] Database updates correctly
- [ ] Error messages display properly

---

## 🚀 DEPLOYMENT READINESS CHECKLIST

- [ ] All critical fixes applied
- [ ] Rate limiting enabled
- [ ] Account lockout working
- [ ] Password reset email sent successfully
- [ ] HTTPS enforced in production
- [ ] Database backups created
- [ ] Security audit completed
- [ ] All tests passing (29/50)
- [ ] Load testing completed
- [ ] User acceptance testing passed

---

## 📞 SUPPORT REFERENCES

- [Full Test Report](TEST_EXECUTION_REPORT.md)
- [Analysis Document](TEST_RESULTS_ANALYSIS.md)
- [Visual Summary](TEST_SUMMARY_VISUAL.md)
- [Auto Test Suite](test_login_suite.py)

