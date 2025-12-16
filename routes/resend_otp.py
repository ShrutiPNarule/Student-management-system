from flask import redirect, url_for, flash, session
from app import app
from routes.email_utils import send_otp_email
from datetime import datetime, timedelta
import random


OTP_COOLDOWN_SECONDS = 60


@app.route("/resend-otp")
def resend_otp():

    # Must be in OTP flow
    if "pending_user_email" not in session:
        flash("Session expired. Please login again.", "error")
        return redirect(url_for("login"))

    # Cooldown check
    next_allowed_time = session.get("otp_resend_at")
    now = datetime.utcnow()

    if next_allowed_time and now < datetime.fromisoformat(next_allowed_time):
        remaining = int((datetime.fromisoformat(next_allowed_time) - now).total_seconds())
        flash(f"Please wait {remaining} seconds before resending OTP.", "error")
        return redirect(url_for("verify_otp"))

    # Generate new OTP
    otp = random.randint(100000, 999999)

    session["login_otp"] = str(otp)
    session["otp_expires_at"] = (now + timedelta(minutes=5)).isoformat()
    session["otp_resend_at"] = (now + timedelta(seconds=OTP_COOLDOWN_SECONDS)).isoformat()

    try:
        send_otp_email(session["pending_user_email"], otp)
        flash("New OTP sent to your email.", "success")
    except Exception:
        flash("Could not resend OTP. Try again later.", "error")

    return redirect(url_for("verify_otp"))
