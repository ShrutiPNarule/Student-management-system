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

    # Clerk can edit (creates approval request) or admin/superadmin can edit directly
    if session.get("role") not in ["admin", "clerk", "superadmin"]:
        flash("Unauthorized. Only admin/clerk can edit student information.", "error")
        return redirect(url_for("index"))

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
        category = request.form.get("category", "").strip()

        # ---------- BASIC VALIDATION ----------
        if not name or not roll_no or not college or not phone or not email or not dob or not birth_place or not category:
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
            marks5 = int(request.form.get("marks5") or 0)
            marks6 = int(request.form.get("marks6") or 0)
            marks7 = int(request.form.get("marks7") or 0)
            marks8 = int(request.form.get("marks8") or 0)

            for m in [marks_10th, marks_12th, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8]:
                if m < 0 or m > 100:
                    raise ValueError

        except ValueError:
            flash("Marks must be numbers between 0 and 100.", "error")
            return redirect(url_for("update_student_data", student_id=student_id))

        try:
            # ---------- GET CURRENT STUDENT'S USER ID ----------
            cur.execute("""
                SELECT user_id FROM students_master WHERE id = %s AND is_deleted = FALSE
            """, (student_id,))
            current_user_result = cur.fetchone()
            if not current_user_result:
                flash("Student not found.", "error")
                conn.rollback()
                cur.close()
                return redirect(url_for("index"))
            
            current_user_id = current_user_result[0]
            
            # ---------- DUPLICATE CHECK (EXCEPT SELF) ----------
            # Check enrollment_no (only if different from current)
            cur.execute("""
                SELECT id FROM students_master
                WHERE enrollment_no = %s
                  AND id != %s
                  AND is_deleted = FALSE
            """, (roll_no, student_id))
            
            if cur.fetchone():
                flash("Roll number already exists for another student.", "error")
                return redirect(url_for("update_student_data", student_id=student_id))
            
            # Check email (only if different from current user's email)
            cur.execute("""
                SELECT id FROM users_master
                WHERE email = %s
                  AND id != %s
            """, (email, current_user_id))
            
            if cur.fetchone():
                flash("Email already exists for another user.", "error")
                return redirect(url_for("update_student_data", student_id=student_id))

            # Get current user's ID
            cur.execute("SELECT id FROM users_master WHERE email = %s", (session["user_email"],))
            user_result = cur.fetchone()
            if not user_result:
                flash("User not found.", "error")
                conn.rollback()
                return redirect(url_for("index"))
            
            user_id = user_result[0]

            # Prepare new data
            new_data = {
                "name": name,
                "enrollment_no": roll_no,
                "college": college,
                "phone": phone,
                "email": email,
                "dob": dob,
                "birth_place": birth_place,
                "category": category,
                "marks_10th": marks_10th,
                "marks_12th": marks_12th,
                "marks1": marks1,
                "marks2": marks2,
                "marks3": marks3,
                "marks4": marks4,
                "marks5": marks5,
                "marks6": marks6,
                "marks7": marks7,
                "marks8": marks8
            }

            # Get original data for backup
            cur.execute("""
                SELECT 
                    u.name, s.enrollment_no, u.email, u.phone, u.dob, u.birth_place, u.category,
                    m.marks_10th, m.marks_12th, m.marks1, m.marks2, m.marks3, m.marks4,
                    m.marks5, m.marks6, m.marks7, m.marks8
                FROM students_master s
                LEFT JOIN users_master u ON s.user_id = u.id
                LEFT JOIN student_marks m ON s.id = m.student_id
                WHERE s.id = %s
            """, (student_id,))
            original = cur.fetchone()
            
            original_data = {}
            if original:
                original_data = {
                    "name": original[0],
                    "enrollment_no": original[1],
                    "email": original[2],
                    "phone": original[3],
                    "dob": str(original[4]) if original[4] else None,
                    "birth_place": original[5],
                    "category": original[6],
                    "marks_10th": original[7],
                    "marks_12th": original[8],
                    "marks1": original[9],
                    "marks2": original[10],
                    "marks3": original[11],
                    "marks4": original[12],
                    "marks5": original[13],
                    "marks6": original[14],
                    "marks7": original[15],
                    "marks8": original[16]
                }

            print(f"[EDIT REQUEST] Creating pending change request for student {student_id}")
            print(f"[EDIT REQUEST] User ID: {user_id}")
            print(f"[EDIT REQUEST] New data: {new_data}")
            
            # Insert into pending_changes table with 'pending' status
            cur.execute("""
                INSERT INTO pending_changes 
                (change_type, student_id, data, original_data, created_by, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ("edit_student", student_id, json.dumps(new_data), json.dumps(original_data), user_id, "pending"))

            conn.commit()
            print(f"[EDIT REQUEST] Pending change created successfully for student {student_id}")
            
            # Log the action
            log_action("REQUEST_EDIT", "STUDENT", str(student_id), {"requested_by": user_id})
            
            # Different message based on user role
            if session.get("role") == "clerk":
                flash("Edit request sent to auditor for verification and admin for approval.", "info")
            else:
                flash("Edit request sent for verification and approval.", "info")

        except psycopg2.Error as e:
            conn.rollback()
            print(f"[EDIT ERROR] Database Error: {e}")
            print(f"[EDIT ERROR] Error Code: {e.pgcode}")
            print(f"[EDIT ERROR] Error Details: {e.pgerror}")
            flash(f"Database error occurred: {e.pgerror}", "error")
        except Exception as e:
            conn.rollback()
            print(f"[EDIT ERROR] Unexpected Error: {e}")
            flash(f"An error occurred: {str(e)}", "error")

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
