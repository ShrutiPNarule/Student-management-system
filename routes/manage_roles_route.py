"""
Superadmin Role Management Route
Allows superadmin to view and change user roles
"""
from flask import render_template, request, redirect, url_for, flash, session, abort
from app import app
from db import get_connection
import psycopg2
from routes.log_utils import log_action


@app.route("/manage-roles", methods=["GET"])
def manage_roles():
    """Superadmin views list of users and can change roles"""
    
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get all users
        cur.execute("""
            SELECT id, name, email, role_id
            FROM users_master
            ORDER BY role_id, name
        """)
        
        users_data = cur.fetchall()
        
        # Convert role_id to role name
        users = []
        for user_id, name, email, role_id in users_data:
            # Get role name from role_id
            cur.execute("SELECT name FROM roles_master WHERE id = %s", (role_id,))
            role_result = cur.fetchone()
            role_name = role_result[0] if role_result else "unassigned"
            
            users.append((user_id, name, email, role_name))
        
        cur.close()
        
        return render_template("manage_roles.html", users=users)

    except psycopg2.Error as e:
        print(f"[MANAGE ROLES ERROR] {e}")
        flash("Database error occurred.", "error")
        cur.close()
        return redirect(url_for("index"))


@app.route("/change-role-superadmin/<user_id>", methods=["POST"])
def change_role_superadmin(user_id):
    """Superadmin changes user role"""
    
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        abort(403)

    new_role = request.form.get("new_role", "").strip()
    
    if not new_role or new_role not in ["student", "admin", "auditor", "superadmin"]:
        flash("Invalid role selected.", "error")
        return redirect(url_for("manage_roles"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get role ID
        cur.execute("SELECT id FROM roles_master WHERE name = %s", (new_role,))
        role_result = cur.fetchone()
        if not role_result:
            flash("Role not found.", "error")
            cur.close()
            return redirect(url_for("manage_roles"))
        
        new_role_id = role_result[0]
        
        # Get user's current role
        cur.execute("SELECT role_id FROM users_master WHERE id = %s", (user_id,))
        current_role = cur.fetchone()
        if not current_role:
            flash("User not found.", "error")
            cur.close()
            return redirect(url_for("manage_roles"))
        
        old_role_id = current_role[0]
        
        # Update user role
        cur.execute("""
            UPDATE users_master
            SET role_id = %s
            WHERE id = %s
        """, (new_role_id, user_id))
        
        # Handle student_master sync
        if new_role != "student":
            # If promoted from student, delete from students_master
            cur.execute("""
                DELETE FROM students_master
                WHERE user_id = %s
            """, (user_id,))
        else:
            # If demoted to student, check if entry exists
            cur.execute("SELECT 1 FROM students_master WHERE user_id = %s", (user_id,))
            if not cur.fetchone():
                # Create entry in students_master
                cur.execute("""
                    INSERT INTO students_master (user_id, enrollment_no, current_status)
                    VALUES (%s, %s, %s)
                """, (user_id, f"ST_{user_id}", "active"))
        
        conn.commit()
        
        # Log action
        cur.execute("SELECT name FROM users_master WHERE id = %s", (user_id,))
        user_name = cur.fetchone()[0]
        
        log_action("ROLE_CHANGE", "USER", user_id, {
            "old_role": old_role_id,
            "new_role": new_role_id,
            "user_name": user_name
        })
        
        flash(f"✅ Role changed to {new_role} successfully!", "success")
        
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[ROLE CHANGE ERROR] {e}")
        flash("Error changing role. Please try again.", "error")
    
    finally:
        cur.close()
    
    return redirect(url_for("manage_roles"))
