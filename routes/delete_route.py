from flask import redirect, url_for, flash, session, abort
from app import app
from db import get_connection
import psycopg2
from routes.log_utils import log_action


# ---------------------------------------
# SOFT DELETE: ADMIN ONLY
# ---------------------------------------
@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student_data(student_id):

    # Login check
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    # Role check
    if session.get("role") != "admin":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Soft delete student
        cur.execute("""
            UPDATE students_master
            SET is_deleted = TRUE
            WHERE id = %s AND is_deleted = FALSE
        """, (student_id,))

        # Soft delete related marks
        cur.execute("""
            UPDATE student_marks
            SET is_deleted = TRUE
            WHERE student_id = %s
        """, (student_id,))

        conn.commit()

        # ✅ LOG ACTION (correct usage)
        log_action("DELETE", "STUDENT", str(student_id))

        flash("Student record moved to recycle bin.", "success")

    except psycopg2.Error as err:
        conn.rollback()
        flash(f"Error soft deleting record: {err}", "error")

    finally:
        cur.close()

    return redirect(url_for("index"))
