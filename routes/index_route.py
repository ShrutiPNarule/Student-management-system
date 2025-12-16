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
                s.id, s.name, s.roll_no, s.college, s.phone, s.email,
                m.marks_10th, m.marks_12th, m.marks1, m.marks2, m.marks3, m.marks4
            FROM students_master s
            LEFT JOIN student_marks m ON s.id = m.student_id
            WHERE s.is_deleted = FALSE AND s.email = %s
            ORDER BY s.id;
        """, (user_email,))

    elif role in ("admin", "auditor"):
        cur.execute("""
            SELECT 
                s.id, s.name, s.roll_no, s.college, s.phone, s.email,
                m.marks_10th, m.marks_12th, m.marks1, m.marks2, m.marks3, m.marks4
            FROM students_master s
            LEFT JOIN student_marks m ON s.id = m.student_id
            WHERE s.is_deleted = FALSE
            ORDER BY s.id;
        """)

    else:
        cur.close()
        abort(403)

    students = cur.fetchall()
    cur.close()

    return render_template("index.html", students=students)
