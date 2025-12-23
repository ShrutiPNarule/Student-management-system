from flask import render_template, request, redirect, url_for, flash, session, abort
from db import get_connection
from app import app
import psycopg2
import re
from routes.log_utils import log_action
from werkzeug.security import generate_password_hash


EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


@app.route("/add", methods=["GET", "POST"])
def add_student():

    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        abort(403)

    if request.method == "POST":

        # ---------- FETCH & TRIM ----------
        name = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip()
        college = request.form.get("college", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        dob = request.form.get("dob", "").strip()
        birth_place = request.form.get("birth_place", "").strip()
        religion = request.form.get("religion", "").strip()
        category = request.form.get("category", "").strip()
        caste = request.form.get("caste", "").strip()

        # ---------- BASIC VALIDATION ----------
        if not name or not roll_no or not college or not phone or not email or not dob or not birth_place or not religion or not category:
            flash("All required fields must be filled.", "error")
            return render_template("add_student.html")

        if not re.fullmatch(r"[A-Za-z ]{2,}", name):
            flash("Name must contain only letters.", "error")
            return render_template("add_student.html")

        if not phone.isdigit() or len(phone) != 10:
            flash("Phone number must be exactly 10 digits.", "error")
            return render_template("add_student.html")

        if not re.fullmatch(EMAIL_REGEX, email):
            flash("Invalid email format.", "error")
            return render_template("add_student.html")

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
            return render_template("add_student.html")

        conn = get_connection()
        cur = conn.cursor()

        try:
            # ---------- DUPLICATE CHECK ----------
            cur.execute(
                "SELECT 1 FROM users_master WHERE email = %s",
                (email,)
            )
            if cur.fetchone():
                flash("Email already exists.", "error")
                return render_template("add_student.html")

            # Get student role_id
            cur.execute(
                "SELECT id FROM roles_master WHERE name = %s",
                ("student",),
            )
            role_row = cur.fetchone()
            if not role_row:
                flash("Student role not found in system.", "error")
                return render_template("add_student.html")

            student_role_id = role_row[0]

            # ---------- CREATE USER RECORD ----------
            cur.execute("""
                INSERT INTO users_master (name, email, password, phone, role_id, address, dob, religion, category, caste, birth_place)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (name, email, generate_password_hash(email + roll_no, method="pbkdf2:sha256", salt_length=16), phone, student_role_id, college, dob, religion, category, caste, birth_place))

            user_id = cur.fetchone()[0]

            # ---------- CREATE STUDENT RECORD ----------
            cur.execute("""
                INSERT INTO students_master (user_id, enrollment_no, current_status)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, (user_id, roll_no, "active"))

            student_id = cur.fetchone()[0]

            # ---------- INSERT MARKS ----------
            cur.execute("""
                INSERT INTO student_marks
                    (student_id, marks_10th, marks_12th,
                     marks1, marks2, marks3, marks4)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                marks_10th,
                marks_12th,
                marks1, marks2, marks3, marks4
            ))

            conn.commit()
            
            # Log the action
            log_action("CREATE", "STUDENT", str(student_id), {"name": name, "email": email})
            
            flash("New student added successfully!", "success")

        except psycopg2.Error:
            conn.rollback()
            flash("Database error occurred. Please try again.", "error")

        finally:
            cur.close()

        return redirect(url_for("index"))

    return render_template("add_student.html")
