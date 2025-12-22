from flask import Flask, request, redirect
from dotenv import load_dotenv
from datetime import timedelta
import os

# ---------------- LOAD ENV VARIABLES ----------------
# Loads SECRET_KEY and other values from .env file
load_dotenv()

app = Flask(__name__)

# ---------------- SECRET KEY ----------------
# Never hardcoded – loaded from .env
app.secret_key = os.getenv("SECRET_KEY")

# ---------------- SESSION CONFIG ----------------
# Session expires after inactivity
app.permanent_session_lifetime = timedelta(minutes=30)

# Secure cookie settings
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,   # ✅ Set True when deployed with HTTPS
    SESSION_COOKIE_SAMESITE="Lax"
)

# ---------------- HTTP → HTTPS REDIRECT ----------------
# Enforced only outside debug mode
@app.before_request
def enforce_https_and_capture_redirect():
    # ✅ TC_LOGIN_038: HTTPS redirect in production
    env = os.getenv('ENVIRONMENT', 'development')
    if not request.is_secure and env == 'production':
        return redirect(request.url.replace("http://", "https://"), code=301)
    
    # ✅ TC_LOGIN_027: Capture URL for protected pages
    if request.method == 'GET' and 'user_email' not in session:
        protected_endpoints = ['index', 'add', 'edit', 'delete', 'recycle_bin', 'logs', 'log_route']
        if request.endpoint in protected_endpoints:
            session['next_url'] = request.url
    
    # ✅ TC_LOGIN_014: Check persistent login token
    if 'user_email' not in session:
        token = request.cookies.get('remember_token')
        
        if token:
            from db import get_connection as get_db_conn
            try:
                conn = get_db_conn()
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
            except Exception as e:
                print(f"Persistent token error: {e}")
                pass

# ---------------- RATE LIMITING (BRUTE FORCE PROTECTION) ----------------
# Enable rate limiting for security
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# ---------------- GLOBAL ERROR HANDLING ----------------
# Auth / service failure handling (TC_LOGIN_040)
@app.errorhandler(500)
def handle_auth_error(e):
    return "Authentication service unavailable. Please try again later.", 503

# ---------------- ROUTES ----------------
from routes import *

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
