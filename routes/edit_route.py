from flask import render_template, request, redirect, url_for, flash, session, abort
from app import app
from db import get_connection
import psycopg2
import re
from routes.log_utils import log_action


EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def update_student_data(student_id):

    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "ADMIN":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":

        # ---------- FETCH & TRIM ----------
        name = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip()
        college = request.form.get("college", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()

        # ---------- BASIC VALIDATION ----------
        if not name or not roll_no or not college or not phone or not email:
            flash("All fields are required.", "error")
            return redirect(url_for("update_student_data", student_id=student_id))

        if not re.fullmatch(r"[A-Za-z ]{2,}", name):
            flash("Name must contain only letters.", "error")
            return redirect(url_for("update_student_data", student_id=student_id))

        if not phone.isdigit() or len(phone) != 10:
            flash("Phone number must be exactly 10 digits.", "error")
            return redirect(url_for("update_student_data", student_id=student_id))

        if not re.fullmatch(EMAIL_REGEX, email):
            flash("Invalid email format.", "error")
            return redirect(url_for("update_student_data", student_id=student_id))

        # ---------- MARKS VALIDATION ----------
        try:
            marks_10th = int(request.form.get("marks_10th") or 0)
            marks_12th = int(request.form.get("marks_12th") or 0)
            marks1 = int(request.form.get("marks1") or 0)
            marks2 = int(request.form.get("marks2") or 0)
            marks3 = int(request.form.get("marks3") or 0)
            marks4 = int(request.form.get("marks4") or 0)

            for m in [marks_10th, marks_12th, marks1, marks2, marks3, marks4]:
                if m < 0 or m > 100:
                    raise ValueError

        except ValueError:
            flash("Marks must be numbers between 0 and 100.", "error")
            return redirect(url_for("update_student_data", student_id=student_id))

        try:
            # ---------- DUPLICATE CHECK (EXCEPT SELF) ----------
            cur.execute("""
                SELECT 1 FROM students_master
                WHERE (roll_no = %s OR email = %s)
                  AND id != %s
                  AND is_deleted = FALSE
            """, (roll_no, email, student_id))

            if cur.fetchone():
                flash("Roll number or email already exists.", "error")
                return redirect(url_for("update_student_data", student_id=student_id))

            # ---------- UPDATE MASTER ----------
            cur.execute("""
                UPDATE students_master
                SET name=%s,
                    roll_no=%s,
                    college=%s,
                    phone=%s,
                    email=%s
                WHERE id=%s
                  AND is_deleted = FALSE
            """, (name, roll_no, college, phone, email, student_id))

            # ---------- UPDATE MARKS ----------
            cur.execute("""
                UPDATE student_marks
                SET marks_10th=%s,
                    marks_12th=%s,
                    marks1=%s,
                    marks2=%s,
                    marks3=%s,
                    marks4=%s
                WHERE student_id=%s
            """, (
                marks_10th, marks_12th,
                marks1, marks2, marks3, marks4,
                student_id
            ))

            conn.commit()
            
            # Log the action
            log_action("UPDATE", "STUDENT", str(student_id), {"name": name, "email": email})
            
            flash("Student updated successfully!", "success")

        except psycopg2.Error:
            conn.rollback()
            flash("Database error occurred. Please try again.", "error")

        finally:
            cur.close()

        return redirect(url_for("index"))

    # ---------- GET: FETCH EXISTING DATA ----------
    cur.execute("""
        SELECT 
            s.id, s.name, s.roll_no, s.college, s.phone, s.email,
            m.marks_10th, m.marks_12th, m.marks1, m.marks2, m.marks3, m.marks4
        FROM students_master s
        LEFT JOIN student_marks m ON s.id = m.student_id
        WHERE s.id = %s
          AND s.is_deleted = FALSE
    """, (student_id,))

    student = cur.fetchone()
    cur.close()

    if not student:
        flash("Student not found or record is deleted!", "error")
        return redirect(url_for("index"))

    return render_template("edit_student.html", student=student)
