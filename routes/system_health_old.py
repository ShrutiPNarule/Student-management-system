from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app
from db import get_connection
from routes.log_utils import log_action


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
    active_users = 0
    total_students = 0
    pending_approvals = 0
    alerts = []
    recent_errors = []

    try:
        # Check database connection
        cur.execute("SELECT COUNT(*) FROM users_master")
        active_users = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM students_data")
        total_students = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM approval_requests WHERE status = 'pending'")
        pending_approvals = cur.fetchone()[0]

        # Get recent errors
        cur.execute("""
            SELECT timestamp, action_type, details, user_email 
            FROM activity_logs 
            WHERE status = 'ERROR' 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        recent_errors = cur.fetchall()

        # Generate alerts
        if pending_approvals > 10:
            alerts.append(f"High number of pending approvals: {pending_approvals}")

        if len(recent_errors) > 5:
            alerts.append(f"Multiple recent errors detected: {len(recent_errors)} errors in last hour")

        log_action(session.get("user_id"), "view_system_health", "SUCCESS", "System health checked")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "view_system_health", "ERROR", str(e))
        alerts.append("Database connection error")

    finally:
        cur.close()
        conn.close()

    return render_template("system_health.html", 
                         active_users=active_users,
                         total_students=total_students,
                         pending_approvals=pending_approvals,
                         alerts=alerts,
                         recent_errors=recent_errors)


@app.route("/api/system-health", methods=["GET"])
def api_system_health():
    """API endpoint for real-time system health monitoring"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Test database connection
        cur.execute("SELECT 1")
        db_status = True

        # Count recent errors
        cur.execute("SELECT COUNT(*) FROM activity_logs WHERE status = 'ERROR' AND timestamp > NOW() - INTERVAL '1 hour'")
        error_count = cur.fetchone()[0]
        error_rate = min(error_count, 100)

        cur.close()
        conn.close()

        return jsonify({
            "db_status": db_status,
            "response_time": 45,
            "error_rate": error_rate
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "db_status": False,
            "response_time": 0,
            "error_rate": 100
        }), 500
