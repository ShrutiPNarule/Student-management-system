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
def enforce_https():
    if not request.is_secure and not app.debug:
        return redirect(request.url.replace("http://", "https://"), code=301)

# ---------------- RATE LIMITING (BRUTE FORCE PROTECTION) ----------------
# Optional but recommended (TC_LOGIN_041)
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
except Exception:
    limiter = None   # App still runs if limiter not installed

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
