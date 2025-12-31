# routes/index_route.py

from flask import render_template, session, redirect, url_for, flash, abort
from app import app
from db import get_connection


@app.route("/")
def index():
    if "user_email" not in session:
        session["next_url"] = url_for("index")
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    role = session.get("role")
    user_email = session.get("user_email")

    conn = get_connection()
    cur = conn.cursor()

    if role == "student":
        cur.execute("""
            SELECT 
                id, name, roll_no, address, phone, email, college, category,
                marks_10th, marks_12th, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
            FROM students_data
            WHERE email = %s
            ORDER BY id;
        """, (user_email,))

    elif role in ("admin", "auditor", "superadmin"):
        cur.execute("""
            SELECT 
                id, name, roll_no, address, phone, email, college, category,
                marks_10th, marks_12th, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8
            FROM students_data
            ORDER BY id;
        """)

    else:
        cur.close()
        abort(403)

    students = cur.fetchall()
    cur.close()

    return render_template("index.html", students=students)


@app.route("/dashboard-summary", methods=["GET"])
def dashboard_summary():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") not in ["admin", "auditor", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    dashboard = {
        'total_students': 0,
        'pending_approvals': 0,
        'active_users': 0,
        'deleted_items': 0,
        'avg_gpa': 0,
        'pass_rate': 0,
        'retention_rate': 0,
        'recent_activities': []
    }

    try:
        # Total Students
        cur.execute("SELECT COUNT(*) FROM students_master WHERE is_deleted = FALSE")
        dashboard['total_students'] = cur.fetchone()[0]

        # Pending Approvals
        cur.execute("SELECT COUNT(*) FROM admin_approval_requests WHERE status = 'pending'")
        dashboard['pending_approvals'] = cur.fetchone()[0]

        # Active Users (count of users with roles)
        cur.execute("""
            SELECT COUNT(*) FROM users_master WHERE role_id IS NOT NULL
        """)
        dashboard['active_users'] = cur.fetchone()[0]

        # Deleted Items (soft deleted)
        cur.execute("""
            SELECT COUNT(*) FROM students_master WHERE is_deleted = TRUE
        """)
        dashboard['deleted_items'] = cur.fetchone()[0]

        # Average GPA
        cur.execute("""
            SELECT ROUND(AVG((marks1 + marks2 + marks3 + marks4 + marks5 + marks6 + marks7 + marks8) / 8.0), 2)
            FROM students_data
            WHERE marks1 IS NOT NULL
        """)
        result = cur.fetchone()
        dashboard['avg_gpa'] = result[0] if result[0] else 0

        # Pass Rate
        cur.execute("""
            SELECT ROUND(
                COUNT(CASE WHEN (marks1 + marks2 + marks3 + marks4 + marks5 + marks6 + marks7 + marks8) / 8.0 >= 40 THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0),
                2
            )
            FROM students_data
            WHERE marks1 IS NOT NULL
        """)
        result = cur.fetchone()
        dashboard['pass_rate'] = result[0] if result[0] else 0

        # Retention Rate (students still active)
        cur.execute("""
            SELECT ROUND(
                COUNT(CASE WHEN is_deleted = FALSE THEN 1 END) * 100.0 / 
                NULLIF(COUNT(*), 0),
                2
            )
            FROM students_master
        """)
        result = cur.fetchone()
        dashboard['retention_rate'] = result[0] if result[0] else 0

        # Recent Activities (last 5)
        cur.execute("""
            SELECT 
                TO_CHAR(al.created_at, 'DD-MM-YYYY HH24:MI'),
                al.action || ' - ' || COALESCE(um.name, 'Unknown User')
            FROM activity_log al
            LEFT JOIN users_master um ON al.user_id = um.id
            ORDER BY al.created_at DESC
            LIMIT 5
        """)
        dashboard['recent_activities'] = cur.fetchall()

    except Exception as e:
        print(f"Error generating dashboard: {e}")
        flash(f"Error loading dashboard: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("dashboard_summary.html", dashboard=dashboard)
