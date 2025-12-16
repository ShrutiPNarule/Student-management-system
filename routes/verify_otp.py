from flask import render_template, request, redirect, url_for, flash, session
from app import app
from datetime import datetime


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

        flash("Login successful!", "success")

        # ✅ STEP 2 FIX (TC_LOGIN_027)
        next_url = session.pop("next_url", None)
        return redirect(next_url or url_for("index"))

    return render_template("verify_otp.html")
