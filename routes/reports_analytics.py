from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app
from db import get_connection
from routes.log_utils import log_action


@app.route("/academic-report", methods=["GET"])
def academic_report():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") not in ["auditor", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    report_data = None

    try:
        semester = request.args.get("semester", "")
        college = request.args.get("college", "")

        if semester:
            query = "SELECT * FROM students_data WHERE 1=1"
            params = []

            if college:
                query += " AND college ILIKE %s"
                params.append(f"%{college}%")

            cur.execute(query, params)
            students = cur.fetchall()

            if students:
                total = len(students)
                avg_gpa = sum(s[11] for s in students if s[11]) / total if total > 0 else 0
                pass_count = sum(1 for s in students if s[11] and s[11] >= 6.0)
                pass_rate = (pass_count / total * 100) if total > 0 else 0
                top_score = max(s[11] for s in students if s[11]) if any(s[11] for s in students) else 0

                report_data = {
                    "total_students": total,
                    "avg_gpa": round(avg_gpa, 2),
                    "pass_rate": round(pass_rate, 2),
                    "top_score": round(top_score, 2)
                }

            log_action(session.get("user_id"), "academic_report", "SUCCESS", f"Generated report for semester {semester}")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "academic_report", "ERROR", str(e))
        flash("An error occurred.", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("academic_report.html", report_data=report_data)


@app.route("/category-stats", methods=["GET"])
def category_stats():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") not in ["auditor", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    stats = {}

    try:
        categories = request.args.getlist("categories")
        if not categories:
            categories = ["General", "OBC", "SC", "ST"]

        cur.execute("SELECT COUNT(*) FROM students_data")
        total_count = cur.fetchone()[0]

        for category in categories:
            cur.execute("SELECT * FROM students_data WHERE category = %s", (category,))
            students = cur.fetchall()
            count = len(students)
            percentage = (count / total_count * 100) if total_count > 0 else 0
            avg_gpa = sum(s[11] for s in students if s[11]) / count if count > 0 else 0
            pass_rate = sum(1 for s in students if s[11] and s[11] >= 6.0) / count * 100 if count > 0 else 0

            stats[category] = {
                "count": count,
                "percentage": round(percentage, 2),
                "avg_gpa": round(avg_gpa, 2),
                "pass_rate": round(pass_rate, 2)
            }

        log_action(session.get("user_id"), "category_stats", "SUCCESS", "Generated category statistics")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "category_stats", "ERROR", str(e))
        flash("An error occurred.", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("category_stats.html", stats=stats)
