from flask import redirect, url_for, flash, session, abort, render_template, request
from app import app
from db import get_connection
import psycopg2
from routes.log_utils import log_action


# ---------------------------------------
# DELETE: ADMIN REQUESTS, SUPERADMIN APPROVES
# ---------------------------------------
@app.route("/delete/<student_id>", methods=["GET", "POST"])
def delete_student_data(student_id):

    # Login check
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    # Role check - only admin can request delete
    if session.get("role") != "admin":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    # GET: Show confirmation page
    if request.method == "GET":
        try:
            # Fetch student details
            cur.execute("""
                SELECT 
                    s.id, u.name, s.enrollment_no, u.phone, u.email, u.address
                FROM students_master s
                LEFT JOIN users_master u ON s.user_id = u.id
                WHERE s.id = %s AND s.is_deleted = FALSE
            """, (student_id,))
            
            student = cur.fetchone()
            cur.close()
            
            if not student:
                flash("Student not found or already deleted!", "error")
                return redirect(url_for("index"))
            
            return render_template("delete_student.html", student=student)
        
        except Exception as e:
            print(f"[DELETE GET ERROR] {e}")
            flash("Error loading student data.", "error")
            cur.close()
            return redirect(url_for("index"))

    # POST: Process deletion request
    try:
        # Get admin's user ID
        cur.execute("SELECT id FROM users_master WHERE email = %s", (session["user_email"],))
        admin_id = cur.fetchone()[0]

        # Create approval request instead of directly deleting
        cur.execute("""
            INSERT INTO admin_approval_requests 
            (admin_id, request_type, entity_type, entity_id, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (admin_id, "DELETE", "STUDENT", student_id, "pending"))

        conn.commit()

        # Log action
        log_action("REQUEST_DELETE", "STUDENT", str(student_id), {"requested_by": admin_id})

        flash("Delete request sent to superadmin for approval. Awaiting response.", "info")

    except psycopg2.Error as err:
        conn.rollback()
        flash(f"Error creating delete request: {err}", "error")

    finally:
        cur.close()

    return redirect(url_for("index"))
