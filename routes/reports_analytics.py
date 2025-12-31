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


@app.route("/college-report", methods=["GET"])
def college_report():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") not in ["auditor", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    colleges = []
    report_data = {}

    try:
        # Get all colleges
        cur.execute("SELECT DISTINCT college FROM students_data WHERE college IS NOT NULL ORDER BY college")
        colleges = [row[0] for row in cur.fetchall()]

        # Get selected college from request
        college_name = request.args.get("college_name", "")

        if college_name:
            # Get students from selected college
            cur.execute("SELECT * FROM students_data WHERE college ILIKE %s", (f"%{college_name}%",))
            students = cur.fetchall()

            if students:
                total = len(students)
                avg_gpa = sum(s[11] for s in students if s[11]) / total if total > 0 else 0
                pass_count = sum(1 for s in students if s[11] and s[11] >= 6.0)
                pass_rate = (pass_count / total * 100) if total > 0 else 0
                top_score = max(s[11] for s in students if s[11]) if any(s[11] for s in students) else 0
                low_score = min(s[11] for s in students if s[11]) if any(s[11] for s in students) else 0

                report_data[college_name] = {
                    "total": total,
                    "avg_gpa": round(avg_gpa, 2),
                    "pass_rate": round(pass_rate, 2),
                    "top_score": round(top_score, 2),
                    "low_score": round(low_score, 2)
                }

            log_action(session.get("user_id"), "college_report", "SUCCESS", f"Generated report for college: {college_name}")
        else:
            # Get all colleges data
            for college in colleges:
                cur.execute("SELECT * FROM students_data WHERE college ILIKE %s", (f"%{college}%",))
                students = cur.fetchall()

                if students:
                    total = len(students)
                    avg_gpa = sum(s[11] for s in students if s[11]) / total if total > 0 else 0
                    pass_count = sum(1 for s in students if s[11] and s[11] >= 6.0)
                    pass_rate = (pass_count / total * 100) if total > 0 else 0
                    top_score = max(s[11] for s in students if s[11]) if any(s[11] for s in students) else 0
                    low_score = min(s[11] for s in students if s[11]) if any(s[11] for s in students) else 0

                    report_data[college] = {
                        "total": total,
                        "avg_gpa": round(avg_gpa, 2),
                        "pass_rate": round(pass_rate, 2),
                        "top_score": round(top_score, 2),
                        "low_score": round(low_score, 2)
                    }

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "college_report", "ERROR", str(e))
        flash("An error occurred.", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("college_report.html", colleges=colleges, report_data=report_data)


@app.route("/attendance-report", methods=["GET"])
def attendance_report():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") not in ["admin", "auditor", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    low_attendance = []

    try:
        from_date = request.args.get("from_date", "")
        to_date = request.args.get("to_date", "")
        threshold = request.args.get("threshold", "75")

        if from_date and to_date:
            try:
                threshold_val = float(threshold) if threshold else 75
            except:
                threshold_val = 75

            query = """
                SELECT 
                    sm.enrollment_no,
                    um.name,
                    ROUND((ar.present_days::numeric / (ar.present_days + ar.absent_days) * 100)::numeric, 2) as attendance_pct,
                    ar.present_days,
                    ar.absent_days,
                    ar.leave_days
                FROM attendance_records ar
                JOIN students_master sm ON ar.student_id = sm.id
                JOIN users_master um ON sm.user_id = um.id
                WHERE ar.attendance_month >= %s AND ar.attendance_month <= %s
                AND (ar.present_days::numeric / (ar.present_days + ar.absent_days) * 100) < %s
                ORDER BY (ar.present_days::numeric / (ar.present_days + ar.absent_days) * 100) ASC
            """
            
            cur.execute(query, (from_date, to_date, threshold_val))
            low_attendance = cur.fetchall()

            log_action(session.get("user_id"), "attendance_report", "SUCCESS", 
                      f"Generated attendance report from {from_date} to {to_date}")
        
    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "attendance_report", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("attendance_report.html", low_attendance=low_attendance)


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
