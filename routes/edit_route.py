from flask import render_template, request, redirect, url_for, flash, session, abort
from app import app
from db import get_connection
import psycopg2
import re
import json
from routes.log_utils import log_action


EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


@app.route("/edit/<student_id>", methods=["GET", "POST"])
def update_student_data(student_id):

    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
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
        dob = request.form.get("dob", "").strip()
        birth_place = request.form.get("birth_place", "").strip()
        religion = request.form.get("religion", "").strip()
        category = request.form.get("category", "").strip()
        caste = request.form.get("caste", "").strip()

        # ---------- BASIC VALIDATION ----------
        if not name or not roll_no or not college or not phone or not email or not dob or not birth_place or not religion or not category:
            flash("All required fields must be filled.", "error")
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
            # Check for duplicate enrollment_no or email in users_master
            cur.execute("""
                SELECT 1 FROM students_master s
                JOIN users_master u ON s.user_id = u.id
                WHERE (s.enrollment_no = %s OR u.email = %s)
                  AND s.id != %s
                  AND s.is_deleted = FALSE
            """, (roll_no, email, student_id))

            if cur.fetchone():
                flash("Roll number or email already exists.", "error")
                return redirect(url_for("update_student_data", student_id=student_id))

            # Get admin's user ID
            cur.execute("SELECT id FROM users_master WHERE email = %s", (session["user_email"],))
            admin_result = cur.fetchone()
            if not admin_result:
                flash("Admin user not found.", "error")
                conn.rollback()
                return redirect(url_for("index"))
            
            admin_id = admin_result[0]

            # Prepare action data
            action_data = {
                "name": name,
                "enrollment_no": roll_no,
                "college": college,
                "phone": phone,
                "email": email,
                "dob": dob,
                "birth_place": birth_place,
                "religion": religion,
                "category": category,
                "caste": caste,
                "marks_10th": marks_10th,
                "marks_12th": marks_12th,
                "marks1": marks1,
                "marks2": marks2,
                "marks3": marks3,
                "marks4": marks4
            }

            # Create approval request instead of directly updating
            cur.execute("""
                INSERT INTO admin_approval_requests 
                (admin_id, request_type, entity_type, entity_id, action_data, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (admin_id, "EDIT", "STUDENT", student_id, json.dumps(action_data), "pending"))

            conn.commit()
            
            # Log the action
            log_action("REQUEST_EDIT", "STUDENT", str(student_id), {"requested_by": admin_id})
            
            flash("Edit request sent to superadmin for approval. Awaiting response.", "info")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"[EDIT ERROR] Database Error: {e}")
            print(f"[EDIT ERROR] Error Code: {e.pgcode}")
            print(f"[EDIT ERROR] Error Details: {e.pgerror}")
            flash("Database error occurred. Please try again.", "error")

        finally:
            cur.close()

        return redirect(url_for("index"))

    # ---------- GET: FETCH EXISTING DATA ----------
    cur.execute("""
        SELECT 
            s.id, u.name, s.enrollment_no, u.phone, u.email, u.address,
            m.marks_10th, m.marks_12th, m.marks1, m.marks2, m.marks3, m.marks4,
            u.dob, u.birth_place, u.religion, u.category, u.caste
        FROM students_master s
        LEFT JOIN users_master u ON s.user_id = u.id
        LEFT JOIN student_marks m ON s.id = m.student_id
        WHERE s.id = %s
    """, (student_id,))

    student = cur.fetchone()
    cur.close()

    if not student:
        flash("Student not found or record is deleted!", "error")
        return redirect(url_for("index"))

    return render_template("edit_student.html", student=student)
