"""
Role Management Route
Handles changing user roles from student to admin/auditor/superadmin
When a student is promoted to admin/auditor/superadmin:
  - DELETE from students_master
  - KEEP in users_master (update role_id)
When someone is demoted back to student:
  - CREATE entry in students_master
  - KEEP in users_master
"""
from flask import render_template, request, redirect, url_for, flash, session, abort
from app import app
from db import get_connection
import psycopg2
from routes.log_utils import log_action


@app.route("/change-role/<user_id>", methods=["GET", "POST"])
def change_user_role(user_id):
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    # Only admin or superadmin can change roles
    if session.get("role") not in ["admin", "superadmin"]:
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        new_role = request.form.get("role", "").strip().lower()

        # Validate role exists
        if new_role not in ["student", "admin", "superadmin", "auditor"]:
            flash("Invalid role selected.", "error")
            return redirect(url_for("index"))

        try:
            # Get current user info
            cur.execute(
                """
                SELECT u.id, u.name, u.role_id, r.name as current_role
                FROM users_master u
                LEFT JOIN roles_master r ON u.role_id = r.id
                WHERE u.id = %s
                """,
                (user_id,),
            )
            user_info = cur.fetchone()

            if not user_info:
                flash("User not found.", "error")
                return redirect(url_for("index"))

            user_id, user_name, current_role_id, current_role = user_info

            # Get new role_id
            cur.execute(
                "SELECT id FROM roles_master WHERE name = %s",
                (new_role,),
            )
            new_role_row = cur.fetchone()
            if not new_role_row:
                flash(f"Role '{new_role}' not found in database.", "error")
                return redirect(url_for("index"))

            new_role_id = new_role_row[0]

            # If changing FROM student role
            if current_role == "student":
                # DELETE from students_master
                cur.execute(
                    "DELETE FROM students_master WHERE user_id = %s",
                    (user_id,),
                )
                flash_msg = (
                    f"✅ User '{user_name}' promoted from student. "
                    f"Removed from students_master table."
                )

            # If changing TO student role (demotion)
            elif new_role == "student":
                # CREATE entry in students_master
                cur.execute(
                    """
                    INSERT INTO students_master (user_id, current_status)
                    VALUES (%s, %s)
                    """,
                    (user_id, "active"),
                )
                flash_msg = (
                    f"✅ User '{user_name}' demoted to student. "
                    f"Created entry in students_master table."
                )

            else:
                # Changing between admin/auditor/superadmin
                flash_msg = f"✅ User '{user_name}' role changed to {new_role}."

            # Update role_id in users_master
            cur.execute(
                "UPDATE users_master SET role_id = %s WHERE id = %s",
                (new_role_id, user_id),
            )

            conn.commit()

            # Log the action
            log_action(
                "ROLE_CHANGE",
                "USER",
                str(user_id),
                {
                    "user_name": user_name,
                    "old_role": current_role,
                    "new_role": new_role,
                },
            )

            flash(flash_msg, "success")
            return redirect(url_for("index"))

        except psycopg2.Error as e:
            conn.rollback()
            print(f"ROLE CHANGE ERROR: {e}")
            flash("Database error occurred while changing role.", "error")
            return redirect(url_for("index"))

        finally:
            cur.close()

    # GET: Show current user info and role options
    try:
        cur.execute(
            """
            SELECT u.id, u.name, u.email, r.name as current_role
            FROM users_master u
            LEFT JOIN roles_master r ON u.role_id = r.id
            WHERE u.id = %s
            """,
            (user_id,),
        )
        user_info = cur.fetchone()

        if not user_info:
            flash("User not found.", "error")
            return redirect(url_for("index"))

        # Get all available roles
        cur.execute("SELECT name FROM roles_master ORDER BY name")
        available_roles = [row[0] for row in cur.fetchall()]

        cur.close()
        return render_template(
            "change_role.html",
            user_id=user_id,
            user_name=user_info[1],
            user_email=user_info[2],
            current_role=user_info[3],
            available_roles=available_roles,
        )

    except psycopg2.Error as e:
        print(f"ROLE FETCH ERROR: {e}")
        flash("Database error occurred.", "error")
        return redirect(url_for("index"))
