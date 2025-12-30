# routes/index_route.py

from flask import render_template, session, redirect, url_for, flash, abort
from app import app
from db import get_connection


@app.route("/")
def index():
    if "user_email" not in session:
        session["next_url"] = url_for("index")
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    role = session.get("role")
    user_email = session.get("user_email")

    conn = get_connection()
    cur = conn.cursor()

    if role == "student":
        cur.execute("""
            SELECT 
                id, name, roll_no, address, phone, email, college, category,
                marks_10th, marks_12th, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
            FROM students_data
            WHERE email = %s
            ORDER BY id;
        """, (user_email,))

    elif role in ("admin", "auditor", "superadmin"):
        cur.execute("""
            SELECT 
                id, name, roll_no, address, phone, email, college, category,
                marks_10th, marks_12th, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
            FROM students_data
            ORDER BY id;
        """)

    else:
        cur.close()
        abort(403)

    students = cur.fetchall()
    cur.close()

    return render_template("index.html", students=students)
