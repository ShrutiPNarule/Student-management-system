from flask import render_template, request, flash, redirect, url_for
from app import app

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        # We do NOT reveal if email exists (security best practice)
        flash(
            "If the email is registered, a password reset link has been sent.",
            "success"
        )
        return redirect(url_for("login"))

    return render_template("forgot_password.html")
