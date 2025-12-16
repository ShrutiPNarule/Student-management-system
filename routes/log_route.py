# routes/log_route.py

from flask import render_template, session, redirect, url_for, flash, abort
from app import app
from db import get_connection


# ---------------- ACTIVITY LOGS PAGE: AUDITOR ONLY ----------------
@app.route("/logs")
def logs():

    # Login check
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    # Role check
    if session.get("role") != "AUDITOR":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT log_id, user_email, role_name, action, details, created_at
        FROM activity_logs
        ORDER BY created_at DESC;
    """)

    logs = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("logs.html", logs=logs)
