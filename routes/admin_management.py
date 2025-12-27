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
            SELECT u.id, u.name, u.email, u.phone, r.name as role, u.is_active, u.last_login
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
            query += " AND u.is_active = %s"
            params.append(status_filter == "active")

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


@app.route("/toggle-user-status/<int:user_id>", methods=["POST"])
def toggle_user_status(user_id):
    if "user_email" not in session or session.get("role") != "superadmin":
        return {"error": "Unauthorized"}, 403

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT is_active FROM users_master WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if not user:
            return {"error": "User not found"}, 404

        new_status = not user[0]
        cur.execute(
            "UPDATE users_master SET is_active = %s, updated_at = NOW() WHERE id = %s",
            (new_status, user_id)
        )
        conn.commit()

        log_action(session.get("user_id"), "toggle_user_status", "SUCCESS", f"User {user_id} status: {new_status}")
        return {"success": True}, 200

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        return {"error": str(e)}, 500

    finally:
        cur.close()
        conn.close()


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

        query = "SELECT timestamp, user_email, action_type, details, status, ip_address FROM activity_logs WHERE 1=1"
        params = []

        if from_date:
            query += " AND timestamp >= %s"
            params.append(from_date)

        if to_date:
            query += " AND timestamp <= %s"
            params.append(to_date + " 23:59:59")

        if user_email:
            query += " AND user_email = %s"
            params.append(user_email)

        if action_type:
            query += " AND action_type ILIKE %s"
            params.append(f"%{action_type}%")

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY timestamp DESC LIMIT 1000"
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
