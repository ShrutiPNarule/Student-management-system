# routes/recycle_bin_route.py

from flask import render_template, redirect, url_for, flash, session, abort
from app import app
from db import get_connection


# ---------------- RECYCLE BIN: AUDITOR ONLY ----------------
@app.route("/recycle_bin")
def recycle_bin():

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
        SELECT 
            s.id,
            s.name,
            s.roll_no,
            s.college,
            s.phone,
            s.email
        FROM students_master s
        WHERE s.is_deleted = TRUE
        ORDER BY s.id;
    """)

    deleted_students = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("recycle_bin.html", deleted_students=deleted_students)
