from flask import redirect, url_for, flash, session
from app import app

@app.route("/logout")
def logout():
    session.clear()
    session.permanent = False   # 🔑 explicitly disable Remember Me
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))
