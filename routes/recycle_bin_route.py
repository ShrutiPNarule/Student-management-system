# routes/recycle_bin_route.py

from flask import render_template, redirect, url_for, flash, session, abort, request
from app import app
from db import get_connection
from routes.log_utils import log_action


# ============== RECYCLE BIN: AUDITOR & SUPERADMIN ==============
@app.route("/recycle_bin")
def recycle_bin():

    # Login check
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    # Role check - auditor or superadmin
    if session.get("role") not in ["auditor", "superadmin"]:
        abort(403)

    conn = get_connection()
    cur = conn.cursor()
    deleted_students = []
    deleted_users = []
    total_deleted = 0

    try:
        # Get deleted students
        cur.execute("""
            SELECT 
                sm.id,
                COALESCE(um.name, 'Unknown') AS name,
                COALESCE(sm.enrollment_no, '-') AS roll_no,
                COALESCE(cc.name, '-') AS college,
                COALESCE(um.phone, '-') AS phone,
                COALESCE(um.email, '-') AS email,
                TO_CHAR(sm.updated_at, 'DD-MM-YYYY') as deleted_date
            FROM students_master sm
            LEFT JOIN users_master um ON sm.user_id = um.id
            LEFT JOIN college_enrollment ce ON sm.id = ce.student_id
            LEFT JOIN colleges_master cc ON ce.college_id = cc.id
            WHERE sm.is_deleted = TRUE
            ORDER BY sm.updated_at DESC
        """)
        deleted_students = cur.fetchall()

        # Get deleted users (if superadmin)
        if session.get("role") == "superadmin":
            cur.execute("""
                SELECT 
                    u.id,
                    u.name,
                    u.email,
                    COALESCE(u.phone, '-') as phone,
                    COALESCE(r.name, '-') as role,
                    TO_CHAR(u.deleted_at, 'DD-MM-YYYY HH24:MI') as deleted_date,
                    COALESCE(u.deletion_reason, '-') as reason
                FROM users_master u
                LEFT JOIN roles_master r ON u.role_id = r.id
                WHERE u.is_deleted = TRUE
                ORDER BY u.deleted_at DESC
            """)
            deleted_users = cur.fetchall()

        total_deleted = len(deleted_students) + len(deleted_users)

        log_action(session.get("user_id"), "recycle_bin", "SUCCESS", 
                  f"Viewed recycle bin - {total_deleted} deleted items")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "recycle_bin", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("recycle_bin.html", deleted_students=deleted_students, 
                         deleted_users=deleted_users, total_deleted=total_deleted)


# ============== RESTORE STUDENT ==============
@app.route("/restore/<student_id>", methods=["GET", "POST"])
def restore_student(student_id):
    
    # Login check
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    # Role check
    if session.get("role") not in ["auditor", "superadmin"]:
        abort(403)

    if request.method == "POST":
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            # Restore the student record
            cur.execute("""
                UPDATE students_master
                SET is_deleted = FALSE
                WHERE id = %s;
            """, (student_id,))
            
            conn.commit()
            log_action(session.get("user_id"), "recycle_bin", "SUCCESS", 
                      f"Restored student {student_id}")
            cur.close()
            conn.close()
            
            flash(f"Student {student_id} has been successfully restored!", "success")
            return redirect(url_for("recycle_bin"))
        
        except Exception as e:
            print(f"Error restoring student: {e}")
            log_action(session.get("user_id"), "recycle_bin", "ERROR", 
                      f"Failed to restore student {student_id}: {str(e)}")
            flash("Error restoring student. Please try again.", "error")
            return redirect(url_for("recycle_bin"))
    
    # GET request - show confirmation form
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                sm.id,
                COALESCE(um.name, '') AS name,
                COALESCE(sm.enrollment_no, '') AS roll_no,
                COALESCE(um.email, '') AS email
            FROM students_master sm
            LEFT JOIN users_master um ON sm.user_id = um.id
            WHERE sm.id = %s AND sm.is_deleted = TRUE;
        """, (student_id,))
        
        student = cur.fetchone()
        cur.close()
        conn.close()
        
        if not student:
            flash("Student not found in recycle bin.", "error")
            return redirect(url_for("recycle_bin"))
        
        return render_template("restore_student.html", student=student)
    
    except Exception as e:
        print(f"Error fetching student: {e}")
        flash("Error retrieving student details.", "error")
        return redirect(url_for("recycle_bin"))
