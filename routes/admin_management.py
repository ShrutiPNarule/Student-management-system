from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
from routes.log_utils import log_action


@app.route("/user-management", methods=["GET"])
def user_management():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    users = []

    try:
        search = request.args.get("search", "").strip()
        role_filter = request.args.get("role_filter", "")
        status_filter = request.args.get("status_filter", "")

        query = """
            SELECT u.id, u.name, u.email, u.phone, r.name as role, u.created_at
            FROM users_master u
            LEFT JOIN roles_master r ON u.role_id = r.id
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (u.name ILIKE %s OR u.email ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        if role_filter:
            query += " AND r.name = %s"
            params.append(role_filter)

        if status_filter:
            query += " AND r.name IS NOT NULL" if status_filter == "active" else " AND r.name IS NULL"

        query += " ORDER BY u.name ASC"
        cur.execute(query, params)
        users = cur.fetchall()

        log_action(session.get("user_id"), "user_management", "SUCCESS", f"Viewed {len(users)} users")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "user_management", "ERROR", str(e))
        flash("An error occurred.", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("user_management.html", users=users)


@app.route("/toggle-user-status/<user_id>", methods=["POST"])
def toggle_user_status(user_id):
    if "user_email" not in session or session.get("role") != "superadmin":
        return {"error": "Unauthorized"}, 403

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Check current role status
        cur.execute("SELECT role_id FROM users_master WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if not user:
            return {"error": "User not found"}, 404

        # Toggle: if role_id is set, clear it (deactivate); if null, set to student role (activate)
        if user[0] is not None:
            # Deactivate: clear role
            cur.execute(
                "UPDATE users_master SET role_id = NULL, updated_at = NOW() WHERE id = %s",
                (user_id,)
            )
            status = "deactivated"
        else:
            # Activate: set to student role
            cur.execute(
                "SELECT id FROM roles_master WHERE name = 'student' LIMIT 1"
            )
            student_role = cur.fetchone()
            if student_role:
                cur.execute(
                    "UPDATE users_master SET role_id = %s, updated_at = NOW() WHERE id = %s",
                    (student_role[0], user_id)
                )
                status = "activated"
            else:
                return {"error": "Student role not found"}, 500

        conn.commit()

        log_action(session.get("user_id"), "toggle_user_status", "SUCCESS", f"User {user_id} {status}")
        return {"success": True}, 200

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return {"error": str(e)}, 500

    finally:
        cur.close()
        conn.close()


@app.route("/account-activation", methods=["GET", "POST"])
def account_activation():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    users = []

    try:
        # Handle activation/deactivation
        if request.method == "POST":
            user_id = request.form.get("user_id")
            action = request.form.get("action")

            if action == "activate":
                # Set role to student
                cur.execute("SELECT id FROM roles_master WHERE name = 'student' LIMIT 1")
                student_role = cur.fetchone()
                if student_role:
                    cur.execute(
                        "UPDATE users_master SET role_id = %s, updated_at = NOW() WHERE id = %s",
                        (student_role[0], user_id)
                    )
                    conn.commit()
                    log_action(session.get("user_id"), "account_activation", "SUCCESS", f"Account {user_id} activated")
                    flash(f"Account activated successfully.", "success")

            elif action == "deactivate":
                # Clear role
                cur.execute(
                    "UPDATE users_master SET role_id = NULL, updated_at = NOW() WHERE id = %s",
                    (user_id,)
                )
                conn.commit()
                log_action(session.get("user_id"), "account_activation", "SUCCESS", f"Account {user_id} deactivated")
                flash(f"Account deactivated successfully.", "success")

            return redirect(url_for("account_activation"))

        # Get users with filters
        search = request.args.get("search", "").strip()
        role_filter = request.args.get("role_filter", "")
        status_filter = request.args.get("status_filter", "")

        query = """
            SELECT u.id, u.name, u.email, u.phone, r.name as role,
                   CASE WHEN u.role_id IS NOT NULL THEN 'active' ELSE 'inactive' END as status,
                   TO_CHAR(u.created_at, 'DD-MM-YYYY')
            FROM users_master u
            LEFT JOIN roles_master r ON u.role_id = r.id
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (u.name ILIKE %s OR u.email ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        if role_filter:
            query += " AND r.name = %s"
            params.append(role_filter)

        if status_filter == "active":
            query += " AND u.role_id IS NOT NULL"
        elif status_filter == "inactive":
            query += " AND u.role_id IS NULL"

        query += " ORDER BY u.name ASC"
        cur.execute(query, params)
        users = cur.fetchall()

        log_action(session.get("user_id"), "account_activation", "SUCCESS", 
                  f"Viewed account activation page - {len(users)} users found")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "account_activation", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("account_activation.html", users=users)


@app.route("/account-deletion", methods=["GET", "POST"])
def account_deletion():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    users = []

    try:
        # Handle account deletion
        if request.method == "POST":
            user_id = request.form.get("user_id")
            reason = request.form.get("reason", "").strip()

            if not reason:
                flash("Deletion reason is required.", "error")
                return redirect(url_for("account_deletion"))

            cur.execute(
                """UPDATE users_master 
                   SET is_deleted = TRUE, deleted_by = %s, deleted_at = NOW(), deletion_reason = %s, 
                       updated_at = NOW()
                   WHERE id = %s""",
                (session.get("user_id"), reason, user_id)
            )
            conn.commit()
            log_action(session.get("user_id"), "account_deletion", "SUCCESS", 
                      f"Deleted account {user_id} - Reason: {reason}")
            flash("Account deleted successfully.", "success")
            return redirect(url_for("account_deletion"))

        # Get active users (not deleted)
        search = request.args.get("search", "").strip()
        role_filter = request.args.get("role_filter", "")

        query = """
            SELECT u.id, u.name, u.email, u.phone, r.name as role,
                   TO_CHAR(u.created_at, 'DD-MM-YYYY') as created_date
            FROM users_master u
            LEFT JOIN roles_master r ON u.role_id = r.id
            WHERE u.is_deleted = FALSE
        """
        params = []

        if search:
            query += " AND (u.name ILIKE %s OR u.email ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        if role_filter:
            query += " AND r.name = %s"
            params.append(role_filter)

        query += " ORDER BY u.name ASC"
        cur.execute(query, params)
        users = cur.fetchall()

        log_action(session.get("user_id"), "account_deletion", "SUCCESS", 
                  f"Viewed account deletion page - {len(users)} users found")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "account_deletion", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("account_deletion.html", users=users)


@app.route("/audit-logs", methods=["GET"])
def audit_logs():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    logs = []

    try:
        from_date = request.args.get("from_date", "")
        to_date = request.args.get("to_date", "")
        user_email = request.args.get("user_email", "").strip()
        action_type = request.args.get("action_type", "").strip()
        status = request.args.get("status", "")

        query = """
            SELECT 
                TO_CHAR(al.created_at, 'DD-MM-YYYY HH24:MI:SS') as timestamp,
                um.email as user_email,
                al.action as action_type,
                al.entity_type || ' (' || al.entity_id || ')' as details,
                COALESCE(al.metadata->>'status', 'INFO') as status,
                al.ip_address
            FROM activity_log al
            LEFT JOIN users_master um ON al.user_id = um.id
            WHERE 1=1
        """
        params = []

        if from_date:
            query += " AND al.created_at >= %s"
            params.append(from_date + " 00:00:00")

        if to_date:
            query += " AND al.created_at <= %s"
            params.append(to_date + " 23:59:59")

        if user_email:
            query += " AND um.email ILIKE %s"
            params.append(f"%{user_email}%")

        if action_type:
            query += " AND al.action ILIKE %s"
            params.append(f"%{action_type}%")

        if status:
            query += " AND al.metadata->>'status' = %s"
            params.append(status)

        query += " ORDER BY al.created_at DESC LIMIT 1000"
        cur.execute(query, params)
        logs = cur.fetchall()

        log_action(session.get("user_id"), "view_audit_logs", "SUCCESS", f"Retrieved {len(logs)} logs")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "view_audit_logs", "ERROR", str(e))
        flash("An error occurred.", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("audit_logs.html", logs=logs)

@app.route("/notification-preferences", methods=["GET", "POST"])
def notification_preferences():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") not in ["superadmin", "admin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    user_prefs = {}

    try:
        user_id = session.get("user_id")

        if request.method == "POST":
            # Save notification preferences
            email_approvals = request.form.get("email_approvals") == "on"
            email_approvals_completed = request.form.get("email_approvals_completed") == "on"
            email_daily_summary = request.form.get("email_daily_summary") == "on"
            sms_approvals = request.form.get("sms_approvals") == "on"
            sms_phone = request.form.get("sms_phone", "").strip()
            notification_frequency = request.form.get("notification_frequency", "instant")

            cur.execute("""
                INSERT INTO notification_preferences 
                (user_id, email_approvals, email_approvals_completed, email_daily_summary, 
                 sms_approvals, sms_phone, notification_frequency)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    email_approvals = %s,
                    email_approvals_completed = %s,
                    email_daily_summary = %s,
                    sms_approvals = %s,
                    sms_phone = %s,
                    notification_frequency = %s,
                    updated_at = NOW()
            """, (user_id, email_approvals, email_approvals_completed, email_daily_summary,
                  sms_approvals, sms_phone, notification_frequency,
                  email_approvals, email_approvals_completed, email_daily_summary,
                  sms_approvals, sms_phone, notification_frequency))

            conn.commit()
            log_action(user_id, "update_notification_preferences", "SUCCESS", "Notification preferences updated")
            flash("Notification preferences saved successfully.", "success")

        # Get current preferences
        cur.execute("""
            SELECT email_approvals, email_approvals_completed, email_daily_summary,
                   sms_approvals, sms_phone, notification_frequency
            FROM notification_preferences
            WHERE user_id = %s
        """, (user_id,))

        result = cur.fetchone()
        if result:
            user_prefs = {
                'email_approvals': result[0],
                'email_approvals_completed': result[1],
                'email_daily_summary': result[2],
                'sms_approvals': result[3],
                'sms_phone': result[4],
                'notification_frequency': result[5]
            }

        log_action(user_id, "view_notification_preferences", "SUCCESS", "Viewed notification preferences")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "notification_preferences", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("notification_preferences.html", user_prefs=user_prefs)


@app.route("/approval-audit", methods=["GET"])
def approval_audit():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    user_role = session.get("role")
    if user_role not in ["admin", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    audit_trail = []

    try:
        from_date = request.args.get("from_date", "")
        to_date = request.args.get("to_date", "")
        approver = request.args.get("approver", "")
        status = request.args.get("status", "")

        query = """
            SELECT 
                aar.id as request_id,
                aar.request_type,
                sm.enrollment_no || ' - ' || um_req.name as student,
                um_app.email as approver,
                TO_CHAR(aar.approved_at, 'DD-MM-YYYY HH24:MI') as approval_date,
                aar.status,
                aar.approval_notes
            FROM admin_approval_requests aar
            LEFT JOIN users_master um_req ON aar.admin_id = um_req.id
            LEFT JOIN users_master um_app ON aar.approved_by = um_app.id
            LEFT JOIN students_master sm ON aar.entity_id = sm.id
            WHERE 1=1
        """
        params = []

        if from_date:
            query += " AND aar.created_at >= %s"
            params.append(from_date + " 00:00:00")

        if to_date:
            query += " AND aar.created_at <= %s"
            params.append(to_date + " 23:59:59")

        if approver:
            query += " AND um_app.email ILIKE %s"
            params.append(f"%{approver}%")

        if status:
            query += " AND aar.status = %s"
            params.append(status)

        query += " ORDER BY aar.approved_at DESC NULLS LAST, aar.created_at DESC"
        
        cur.execute(query, params)
        audit_trail = cur.fetchall()

        log_action(session.get("user_id"), "approval_audit", "SUCCESS", 
                  f"Generated approval audit report")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "approval_audit", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("approval_audit.html", audit_trail=audit_trail)


@app.route("/activity-report", methods=["GET"])
def activity_report():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    user_role = session.get("role")
    if user_role not in ["admin", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    activity_log = []

    try:
        from_date = request.args.get("from_date", "")
        to_date = request.args.get("to_date", "")
        user_email = request.args.get("user_email", "")
        action_type = request.args.get("action_type", "")

        query = """
            SELECT 
                TO_CHAR(al.created_at, 'DD-MM-YYYY HH24:MI:SS') as timestamp,
                um.email,
                al.action,
                al.entity_type || ' (' || al.entity_id || ')' as details,
                al.ip_address,
                CASE 
                    WHEN al.metadata->>'status' = 'SUCCESS' THEN 'SUCCESS'
                    WHEN al.metadata->>'status' = 'FAILURE' THEN 'FAILURE'
                    ELSE 'INFO'
                END as status
            FROM activity_log al
            LEFT JOIN users_master um ON al.user_id = um.id
            WHERE 1=1
        """
        params = []

        if from_date:
            query += " AND al.created_at >= %s"
            params.append(from_date + " 00:00:00")

        if to_date:
            query += " AND al.created_at <= %s"
            params.append(to_date + " 23:59:59")

        if user_email:
            query += " AND um.email ILIKE %s"
            params.append(f"%{user_email}%")

        if action_type:
            query += " AND al.action ILIKE %s"
            params.append(f"%{action_type}%")

        query += " ORDER BY al.created_at DESC"
        
        cur.execute(query, params)
        activity_log = cur.fetchall()

        log_action(session.get("user_id"), "activity_report", "SUCCESS", 
                  f"Generated activity report")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "activity_report", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("activity_report.html", activity_log=activity_log)


@app.route("/permission-assignment", methods=["GET"])
def permission_assignment():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    roles = []

    try:
        cur.execute("""
            SELECT id, name, view_student, add_student, delete_student, 
                   change_user_role, add_marks, view_activity_log, 
                   create_application, approve_application
            FROM roles_master
            ORDER BY name ASC
        """)
        roles = cur.fetchall()

        log_action(session.get("user_id"), "permission_assignment", "SUCCESS", 
                  f"Viewed permission assignment page - {len(roles)} roles found")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "permission_assignment", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("permission_assignment.html", roles=roles)


@app.route("/edit-role-permissions/<role_id>", methods=["GET", "POST"])
def edit_role_permissions(role_id):
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    permissions = {}
    role_name = ""

    try:
        # Get current role and permissions
        cur.execute("""
            SELECT id, name, view_student, add_student, delete_student, 
                   change_user_role, add_marks, view_activity_log, 
                   create_application, approve_application
            FROM roles_master
            WHERE id = %s
        """, (role_id,))

        role_data = cur.fetchone()
        if not role_data:
            flash("Role not found.", "error")
            return redirect(url_for("permission_assignment"))

        role_name = role_data[1]
        permissions = {
            'view_student': role_data[2],
            'add_student': role_data[3],
            'delete_student': role_data[4],
            'change_user_role': role_data[5],
            'add_marks': role_data[6],
            'view_activity_log': role_data[7],
            'create_application': role_data[8],
            'approve_application': role_data[9]
        }

        if request.method == "POST":
            # Get checkbox values
            view_student = 'view_student' in request.form
            add_student = 'add_student' in request.form
            delete_student = 'delete_student' in request.form
            change_user_role = 'change_user_role' in request.form
            add_marks = 'add_marks' in request.form
            view_activity_log = 'view_activity_log' in request.form
            create_application = 'create_application' in request.form
            approve_application = 'approve_application' in request.form

            # Update permissions
            cur.execute("""
                UPDATE roles_master
                SET view_student = %s,
                    add_student = %s,
                    delete_student = %s,
                    change_user_role = %s,
                    add_marks = %s,
                    view_activity_log = %s,
                    create_application = %s,
                    approve_application = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (view_student, add_student, delete_student, change_user_role,
                  add_marks, view_activity_log, create_application, 
                  approve_application, role_id))

            conn.commit()
            log_action(session.get("user_id"), "edit_role_permissions", "SUCCESS", 
                      f"Updated permissions for role {role_name}")
            flash(f"Permissions updated successfully for {role_name}.", "success")
            return redirect(url_for("permission_assignment"))

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "edit_role_permissions", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("edit_role_permissions.html", role_name=role_name, permissions=permissions)


@app.route("/ip-management", methods=["GET", "POST"])
def ip_management():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    ips = []

    try:
        # Handle POST actions
        if request.method == "POST":
            action = request.form.get("action")

            if action == "add":
                ip_address = request.form.get("ip_address", "").strip()
                description = request.form.get("description", "").strip()

                if not ip_address:
                    flash("IP address is required.", "error")
                else:
                    try:
                        cur.execute("""
                            INSERT INTO ip_whitelist (ip_address, description, added_by, is_active)
                            VALUES (%s, %s, %s, TRUE)
                        """, (ip_address, description or None, session.get("user_id")))
                        conn.commit()
                        log_action(session.get("user_id"), "ip_management", "SUCCESS", f"Added IP {ip_address}")
                        flash(f"IP address {ip_address} added successfully.", "success")
                    except Exception as e:
                        conn.rollback()
                        flash(f"Error adding IP: {str(e)}", "error")

            elif action == "delete":
                ip_id = request.form.get("ip_id")
                cur.execute("DELETE FROM ip_whitelist WHERE id = %s", (ip_id,))
                conn.commit()
                log_action(session.get("user_id"), "ip_management", "SUCCESS", f"Deleted IP {ip_id}")
                flash("IP address deleted successfully.", "success")

            elif action == "activate":
                ip_id = request.form.get("ip_id")
                cur.execute("UPDATE ip_whitelist SET is_active = TRUE, updated_at = NOW() WHERE id = %s", (ip_id,))
                conn.commit()
                log_action(session.get("user_id"), "ip_management", "SUCCESS", f"Activated IP {ip_id}")
                flash("IP address activated.", "success")

            elif action == "deactivate":
                ip_id = request.form.get("ip_id")
                cur.execute("UPDATE ip_whitelist SET is_active = FALSE, updated_at = NOW() WHERE id = %s", (ip_id,))
                conn.commit()
                log_action(session.get("user_id"), "ip_management", "SUCCESS", f"Deactivated IP {ip_id}")
                flash("IP address deactivated.", "success")

            return redirect(url_for("ip_management"))

        # Get all whitelisted IPs
        cur.execute("""
            SELECT iw.id, iw.ip_address, iw.description, um.email as added_by, 
                   iw.is_active, TO_CHAR(iw.created_at, 'DD-MM-YYYY HH24:MI')
            FROM ip_whitelist iw
            LEFT JOIN users_master um ON iw.added_by = um.id
            ORDER BY iw.created_at DESC
        """)
        ips = cur.fetchall()

        log_action(session.get("user_id"), "ip_management", "SUCCESS", 
                  f"Viewed IP management page - {len(ips)} IPs found")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "ip_management", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("ip_management.html", ips=ips)


@app.route("/session-management", methods=["GET", "POST"])
def session_management():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    sessions = []
    total_active = 0
    total_terminated = 0

    try:
        # Handle POST actions
        if request.method == "POST":
            action = request.form.get("action")

            if action == "terminate":
                session_id = request.form.get("session_id")
                cur.execute(
                    "UPDATE active_sessions SET is_active = FALSE WHERE id = %s",
                    (session_id,)
                )
                conn.commit()
                log_action(session.get("user_id"), "session_management", "SUCCESS", 
                          f"Terminated session {session_id}")
                flash("Session terminated successfully.", "success")
                return redirect(url_for("session_management"))

        # Get filters
        search = request.args.get("search", "").strip()
        status_filter = request.args.get("status", "")

        query = """
            SELECT 
                asess.id,
                um.email,
                um.name,
                asess.ip_address,
                asess.user_agent,
                TO_CHAR(asess.login_time, 'DD-MM-YYYY HH24:MI:SS') as login_time,
                TO_CHAR(asess.last_activity, 'DD-MM-YYYY HH24:MI:SS') as last_activity,
                asess.is_active,
                EXTRACT(HOUR FROM (NOW() - asess.login_time)) || ' hrs ' || 
                EXTRACT(MINUTE FROM (NOW() - asess.login_time))::INT || ' mins' as duration
            FROM active_sessions asess
            JOIN users_master um ON asess.user_id = um.id
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (um.email ILIKE %s OR um.name ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        if status_filter == "active":
            query += " AND asess.is_active = TRUE"
        elif status_filter == "inactive":
            query += " AND asess.is_active = FALSE"

        query += " ORDER BY asess.login_time DESC"
        
        cur.execute(query, params)
        sessions = cur.fetchall()

        # Get statistics
        cur.execute("SELECT COUNT(*) FROM active_sessions WHERE is_active = TRUE")
        total_active = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM active_sessions WHERE is_active = FALSE")
        total_terminated = cur.fetchone()[0]

        log_action(session.get("user_id"), "session_management", "SUCCESS", 
                  f"Viewed session management - {len(sessions)} sessions found")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "session_management", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("session_management.html", sessions=sessions, 
                         total_active=total_active, total_terminated=total_terminated)


@app.route("/security-configuration", methods=["GET", "POST"])
def security_configuration():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    configs = {}

    try:
        # Handle POST actions
        if request.method == "POST":
            action = request.form.get("action")

            if action == "update":
                for key in request.form:
                    if key.startswith("config_"):
                        setting_key = key.replace("config_", "")
                        setting_value = request.form.get(key)
                        
                        cur.execute(
                            """UPDATE security_config 
                               SET setting_value = %s, updated_by = %s, updated_at = NOW()
                               WHERE setting_key = %s""",
                            (setting_value, session.get("user_id"), setting_key)
                        )
                
                conn.commit()
                log_action(session.get("user_id"), "security_configuration", "SUCCESS", 
                          "Updated security configurations")
                flash("Security configurations updated successfully.", "success")
                return redirect(url_for("security_configuration"))

        # Get all security configs
        cur.execute("""
            SELECT setting_key, setting_value, description, setting_type, updated_by, updated_at
            FROM security_config
            ORDER BY setting_key ASC
        """)
        rows = cur.fetchall()
        
        for row in rows:
            configs[row[0]] = {
                'value': row[1],
                'description': row[2],
                'type': row[3],
                'updated_by': row[4],
                'updated_at': row[5]
            }

        log_action(session.get("user_id"), "security_configuration", "SUCCESS", 
                  "Viewed security configuration page")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "security_configuration", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("security_configuration.html", configs=configs)


@app.route("/activity-log-viewer", methods=["GET"])
def activity_log_viewer():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") not in ["auditor", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    logs = []
    total_logs = 0

    try:
        # Get filters
        search = request.args.get("search", "").strip()
        action_filter = request.args.get("action", "").strip()
        from_date = request.args.get("from_date", "").strip()
        to_date = request.args.get("to_date", "").strip()

        query = """
            SELECT 
                al.id,
                al.user_id,
                COALESCE(um.name, 'Unknown') as user_name,
                COALESCE(um.email, 'Unknown') as user_email,
                COALESCE(r.name, 'N/A') as role,
                al.action,
                al.entity_type,
                al.entity_id,
                COALESCE(al.ip_address, '-') as ip_address,
                TO_CHAR(al.created_at, 'DD-MM-YYYY HH24:MI:SS') as timestamp
            FROM activity_log al
            LEFT JOIN users_master um ON al.user_id = um.id
            LEFT JOIN roles_master r ON um.role_id = r.id
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (um.name ILIKE %s OR um.email ILIKE %s OR al.user_id ILIKE %s)"
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

        if action_filter:
            query += " AND al.action ILIKE %s"
            params.append(f"%{action_filter}%")

        if from_date:
            query += " AND DATE(al.created_at) >= %s"
            params.append(from_date)

        if to_date:
            query += " AND DATE(al.created_at) <= %s"
            params.append(to_date)

        query += " ORDER BY al.created_at DESC LIMIT 500"
        
        cur.execute(query, params)
        logs = cur.fetchall()
        total_logs = len(logs)

        log_action(session.get("user_id"), "activity_log_viewer", "SUCCESS", 
                  f"Viewed activity logs - {total_logs} entries found")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "activity_log_viewer", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("activity_log_viewer.html", logs=logs, total_logs=total_logs)


@app.route("/system-health", methods=["GET"])
def system_health():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    metrics = {}

    try:
        # Database status
        try:
            cur.execute("SELECT 1")
            metrics['db_status'] = 'Connected'
            metrics['db_status_color'] = 'success'
        except:
            metrics['db_status'] = 'Disconnected'
            metrics['db_status_color'] = 'error'

        # Table record counts
        cur.execute("SELECT COUNT(*) FROM users_master WHERE is_deleted = FALSE")
        metrics['active_users'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM students_master WHERE is_deleted = FALSE")
        metrics['active_students'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM roles_master")
        metrics['total_roles'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM activity_log")
        metrics['total_logs'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM attendance_records")
        metrics['attendance_records'] = cur.fetchone()[0]

        # Active sessions
        cur.execute("SELECT COUNT(*) FROM active_sessions WHERE is_active = TRUE")
        metrics['active_sessions'] = cur.fetchone()[0]

        # Deleted items
        cur.execute("SELECT COUNT(*) FROM users_master WHERE is_deleted = TRUE")
        metrics['deleted_users'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM students_master WHERE is_deleted = TRUE")
        metrics['deleted_students'] = cur.fetchone()[0]

        # Recent errors (last 24 hours)
        cur.execute("""
            SELECT COUNT(*) FROM activity_log 
            WHERE action = 'ERROR' AND created_at > NOW() - INTERVAL '24 hours'
        """)
        metrics['recent_errors'] = cur.fetchone()[0]

        # Locked accounts
        cur.execute("SELECT COUNT(*) FROM users_master WHERE locked_until IS NOT NULL AND locked_until > NOW()")
        metrics['locked_accounts'] = cur.fetchone()[0]

        # Security configurations
        cur.execute("""
            SELECT setting_key, setting_value FROM security_config 
            WHERE setting_key IN ('enable_2fa', 'enable_ip_whitelist', 'enable_email_verification')
        """)
        security_configs = cur.fetchall()
        metrics['security'] = {row[0]: row[1] for row in security_configs}

        # Performance metrics
        cur.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as log_count
            FROM activity_log
            WHERE created_at > NOW() - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at) DESC
        """)
        metrics['daily_activity'] = cur.fetchall()

        # System info
        from datetime import datetime
        metrics['server_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        metrics['db_version'] = 'PostgreSQL'

        log_action(session.get("user_id"), "system_health", "SUCCESS", 
                  "Viewed system health dashboard")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "system_health", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")
        metrics = {}

    finally:
        cur.close()
        conn.close()

    return render_template("system_health.html", metrics=metrics)