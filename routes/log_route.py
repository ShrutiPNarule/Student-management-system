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
    if session.get("role") != "auditor":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, user_id, action, entity_type, entity_id, metadata, created_at
        FROM activity_log
        ORDER BY created_at DESC;
    """)

    logs = cur.fetchall()
    cur.close()

    return render_template("logs.html", logs=logs)
