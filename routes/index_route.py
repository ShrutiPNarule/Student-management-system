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
                s.id, u.name, s.enrollment_no, u.phone, u.email,
                m.marks_10th, m.marks_12th, m.marks1, m.marks2, m.marks3, m.marks4
            FROM students_master s
            LEFT JOIN users_master u ON s.user_id = u.id
            LEFT JOIN student_marks m ON s.id::INTEGER = m.student_id
            WHERE u.email = %s
            ORDER BY s.id;
        """, (user_email,))

    elif role in ("admin", "auditor"):
        cur.execute("""
            SELECT 
                s.id, u.name, s.enrollment_no, u.phone, u.email,
                m.marks_10th, m.marks_12th, m.marks1, m.marks2, m.marks3, m.marks4
            FROM students_master s
            LEFT JOIN users_master u ON s.user_id = u.id
            LEFT JOIN student_marks m ON s.id::INTEGER = m.student_id
            ORDER BY s.id;
        """)

    else:
        cur.close()
        abort(403)

    students = cur.fetchall()
    cur.close()

    return render_template("index.html", students=students)
