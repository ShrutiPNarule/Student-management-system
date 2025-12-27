from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
from routes.log_utils import log_action


@app.route("/search-students", methods=["GET", "POST"])
def search_students():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))
    
    if session.get("role") not in ["admin", "auditor", "superadmin"]:
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))
    
    results = []
    
    if request.method == "GET":
        try:
            conn = get_connection()
            cur = conn.cursor()
            
            search_name = request.args.get("search_name", "").strip()
            search_roll = request.args.get("search_roll", "").strip()
            search_email = request.args.get("search_email", "").strip()
            search_phone = request.args.get("search_phone", "").strip()
            filter_college = request.args.get("filter_college", "").strip()
            filter_category = request.args.get("filter_category", "").strip()
            gpa_min = request.args.get("gpa_min", "")
            gpa_max = request.args.get("gpa_max", "")
            sort_by = request.args.get("sort_by", "name")
            
            params = []
            query = "SELECT * FROM students_data WHERE 1=1"
            
            if search_name:
                params.append(f"%{search_name}%")
                query += " AND name ILIKE %s"
            if search_roll:
                params.append(f"%{search_roll}%")
                query += " AND roll_no ILIKE %s"
            if search_email:
                params.append(f"%{search_email}%")
                query += " AND email ILIKE %s"
            if search_phone:
                params.append(search_phone)
                query += " AND phone = %s"
            if filter_college:
                params.append(f"%{filter_college}%")
                query += " AND college ILIKE %s"
            if filter_category:
                params.append(filter_category)
                query += " AND category = %s"
            if gpa_min:
                params.append(float(gpa_min))
                query += " AND gpa >= %s"
            if gpa_max:
                params.append(float(gpa_max))
                query += " AND gpa <= %s"
            
            sort_columns = {
                "name": "name ASC",
                "roll_no": "roll_no ASC",
                "gpa": "gpa DESC",
                "created_at": "id DESC"
            }
            query += f" ORDER BY {sort_columns.get(sort_by, 'name ASC')}"
            
            cur.execute(query, params)
            results = cur.fetchall()
            
            cur.close()
            conn.close()
            
            log_action(session.get("user_id"), "search_students", "SUCCESS", f"Found {len(results)} students")
        
        except Exception as e:
            log_action(session.get("user_id"), "search_students", "ERROR", str(e))
            print(f"Error: {e}")
            flash("An error occurred during search.", "error")
    
    return render_template("search_students.html", results=results)


@app.route("/student/<int:student_id>/profile", methods=["GET"])
def student_profile(student_id):
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))
    
    if session.get("role") not in ["admin", "auditor", "superadmin"]:
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM students_data WHERE id = %s", (student_id,))
        student = cur.fetchone()
        
        actions = []
        if student:
            cur.execute("""
                SELECT id, action_type, user_email, timestamp, status
                FROM activity_logs
                WHERE student_id = %s
                ORDER BY timestamp DESC
                LIMIT 10
            """, (student_id,))
            actions = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template("student_profile.html", student=student, actions=actions)
    
    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred.", "error")
        return redirect(url_for("index"))
