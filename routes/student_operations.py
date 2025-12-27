from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
from routes.log_utils import log_action
from datetime import datetime


@app.route("/update-marks/<int:student_id>", methods=["GET", "POST"])
def update_marks(student_id):
    if "user_email" not in session or session.get("role") != "admin":
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM students_data WHERE id = %s", (student_id,))
        student = cur.fetchone()

        if not student:
            flash("Student not found.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            marks_10th = float(request.form.get("marks_10th", 0) or 0)
            marks_12th = float(request.form.get("marks_12th", 0) or 0)
            marks_year1 = float(request.form.get("marks_year1", 0) or 0)
            marks_year2 = float(request.form.get("marks_year2", 0) or 0)
            marks_year3 = float(request.form.get("marks_year3", 0) or 0)
            gpa = float(request.form.get("gpa", 0) or 0)
            reason = request.form.get("reason", "Admin update")

            cur.execute("""
                UPDATE students_data 
                SET marks_10th = %s, marks_12th = %s, marks_year1 = %s, 
                    marks_year2 = %s, marks_year3 = %s, gpa = %s, updated_at = NOW()
                WHERE id = %s
            """, (marks_10th, marks_12th, marks_year1, marks_year2, marks_year3, gpa, student_id))

            conn.commit()
            log_action(session.get("user_id"), "update_marks", "SUCCESS", f"Updated marks for student {student_id}: {reason}")
            flash("Student marks updated successfully!", "success")
            return redirect(url_for("index"))

        return render_template("update_marks.html", student=student)

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "update_marks", "ERROR", str(e))
        flash("An error occurred.", "error")
        return redirect(url_for("index"))

    finally:
        cur.close()
        conn.close()


@app.route("/attendance/<int:student_id>", methods=["GET", "POST"])
def attendance(student_id):
    if "user_email" not in session or session.get("role") != "admin":
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM students_data WHERE id = %s", (student_id,))
        student = cur.fetchone()

        if not student:
            flash("Student not found.", "error")
            return redirect(url_for("index"))

        attendance_summary = {"present": 0, "absent": 0, "leave": 0, "percentage": 0}

        if request.method == "POST":
            from_date = request.form.get("from_date")
            to_date = request.form.get("to_date")

            present = absent = leave = 0
            for i in range(15):
                status = request.form.get(f"status_{i}", "")
                if status == "present":
                    present += 1
                elif status == "absent":
                    absent += 1
                elif status == "leave":
                    leave += 1

            total = present + absent + leave
            percentage = (present / total * 100) if total > 0 else 0

            log_action(session.get("user_id"), "record_attendance", "SUCCESS", 
                      f"Recorded attendance for student {student_id}")
            flash("Attendance recorded successfully!", "success")
            return redirect(url_for("index"))

        cur.execute("""
            SELECT COUNT(*) FROM attendance_records 
            WHERE student_id = %s AND status = %s
        """, (student_id, 'present'))
        attendance_summary["present"] = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM attendance_records 
            WHERE student_id = %s AND status = %s
        """, (student_id, 'absent'))
        attendance_summary["absent"] = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM attendance_records 
            WHERE student_id = %s AND status = %s
        """, (student_id, 'leave'))
        attendance_summary["leave"] = cur.fetchone()[0]

        total = attendance_summary["present"] + attendance_summary["absent"]
        if total > 0:
            attendance_summary["percentage"] = round(attendance_summary["present"] / total * 100, 2)

        return render_template("attendance.html", student=student, attendance_summary=attendance_summary)

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "attendance", "ERROR", str(e))
        flash("An error occurred.", "error")
        return redirect(url_for("index"))

    finally:
        cur.close()
        conn.close()


@app.route("/scholarship/<int:student_id>", methods=["GET", "POST"])
def scholarship(student_id):
    if "user_email" not in session or session.get("role") != "admin":
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM students_data WHERE id = %s", (student_id,))
        student = cur.fetchone()

        if not student:
            flash("Student not found.", "error")
            return redirect(url_for("index"))

        scholarship_history = []

        if request.method == "POST":
            scholarship_type = request.form.get("scholarship_type")
            amount = float(request.form.get("amount", 0))
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            provider = request.form.get("provider", "")
            status = request.form.get("status", "active")
            remarks = request.form.get("remarks", "")

            cur.execute("""
                INSERT INTO scholarships (student_id, type, amount, start_date, end_date, provider, status, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (student_id, scholarship_type, amount, start_date, end_date, provider, status, remarks))

            conn.commit()
            log_action(session.get("user_id"), "add_scholarship", "SUCCESS", 
                      f"Added scholarship for student {student_id}")
            flash("Scholarship saved successfully!", "success")
            return redirect(url_for("index"))

        cur.execute("""
            SELECT id, type, amount, start_date, end_date, provider, status 
            FROM scholarships 
            WHERE student_id = %s 
            ORDER BY start_date DESC
        """, (student_id,))
        scholarship_history = cur.fetchall()

        return render_template("scholarship_form.html", student=student, scholarship_history=scholarship_history)

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "scholarship", "ERROR", str(e))
        flash("An error occurred.", "error")
        return redirect(url_for("index"))

    finally:
        cur.close()
        conn.close()


@app.route("/documents/<int:student_id>", methods=["GET", "POST"])
def documents(student_id):
    if "user_email" not in session or session.get("role") != "admin":
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM students_data WHERE id = %s", (student_id,))
        student = cur.fetchone()

        if not student:
            flash("Student not found.", "error")
            return redirect(url_for("index"))

        documents = []

        if request.method == "POST":
            document_type = request.form.get("document_type")
            issue_date = request.form.get("issue_date")
            expiry_date = request.form.get("expiry_date")
            remarks = request.form.get("remarks", "")
            file = request.files.get("document_file")

            if file:
                filename = f"{student_id}_{document_type}_{datetime.now().timestamp()}"
                # Save file logic here
                cur.execute("""
                    INSERT INTO student_documents (student_id, document_type, filename, issue_date, expiry_date, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (student_id, document_type, filename, issue_date, expiry_date, remarks))

                conn.commit()
                log_action(session.get("user_id"), "upload_document", "SUCCESS", 
                          f"Uploaded document for student {student_id}")
                flash("Document uploaded successfully!", "success")
                return redirect(url_for("index"))

        cur.execute("""
            SELECT id, document_type, created_at 
            FROM student_documents 
            WHERE student_id = %s 
            ORDER BY created_at DESC
        """, (student_id,))
        documents = cur.fetchall()

        return render_template("student_documents.html", student=student, documents=documents)

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "documents", "ERROR", str(e))
        flash("An error occurred.", "error")
        return redirect(url_for("index"))

    finally:
        cur.close()
        conn.close()
