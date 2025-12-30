from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
from routes.log_utils import log_action
from datetime import datetime
import os
from werkzeug.utils import secure_filename


@app.route("/update-marks/<student_id>", methods=["GET", "POST"])
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
            marks_year4 = float(request.form.get("marks_year4", 0) or 0)
            marks_year5 = float(request.form.get("marks_year5", 0) or 0)
            marks_year6 = float(request.form.get("marks_year6", 0) or 0)
            marks_year7 = float(request.form.get("marks_year7", 0) or 0)
            marks_year8 = float(request.form.get("marks_year8", 0) or 0)
            reason = request.form.get("reason", "Admin update")

            cur.execute("""
                UPDATE student_marks 
                SET marks_10th = %s, marks_12th = %s, marks1 = %s, 
                    marks2 = %s, marks3 = %s, marks4 = %s,
                    marks5 = %s, marks6 = %s, marks7 = %s, marks8 = %s
                WHERE student_id = %s
            """, (marks_10th, marks_12th, marks_year1, marks_year2, marks_year3, marks_year4, 
                  marks_year5, marks_year6, marks_year7, marks_year8, student_id))

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


@app.route("/attendance/<student_id>", methods=["GET", "POST"])
def attendance(student_id):
    if "user_email" not in session or session.get("role") != "admin":
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Use student_id as string for all database operations
        sid = str(student_id)
            
        cur.execute("SELECT * FROM students_data WHERE id = %s", (sid,))
        student = cur.fetchone()

        if not student:
            flash("Student not found.", "error")
            return redirect(url_for("index"))

        from datetime import datetime, date
        current_month = date.today().strftime("%Y-%m")

        if request.method == "POST":
            attendance_month = request.form.get("attendance_month")
            try:
                present_days = int(request.form.get("present_days") or 0)
                absent_days = int(request.form.get("absent_days") or 0)
                leave_days = int(request.form.get("leave_days") or 0)
            except ValueError:
                flash("Days must be valid numbers.", "error")
                return redirect(url_for("attendance", student_id=student_id))
                
            remarks = request.form.get("remarks", "")

            # Validate inputs
            if present_days < 0 or absent_days < 0 or leave_days < 0:
                flash("Days cannot be negative.", "error")
                return redirect(url_for("attendance", student_id=student_id))

            try:
                # Convert month string to date (format: YYYY-MM-01)
                month_date = attendance_month + "-01"
                
                # Check if record exists for this month
                cur.execute("""
                    SELECT id FROM attendance_records 
                    WHERE student_id = %s AND attendance_month = %s::DATE
                """, (sid, month_date))
                
                existing = cur.fetchone()
                
                if existing:
                    # Update existing record
                    cur.execute("""
                        UPDATE attendance_records 
                        SET present_days = %s, absent_days = %s, leave_days = %s, 
                            remarks = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE student_id = %s AND attendance_month = %s::DATE
                    """, (present_days, absent_days, leave_days, remarks, sid, month_date))
                else:
                    # Insert new record
                    cur.execute("""
                        INSERT INTO attendance_records 
                        (student_id, attendance_month, present_days, absent_days, leave_days, remarks)
                        VALUES (%s, %s::DATE, %s, %s, %s, %s)
                    """, (sid, month_date, present_days, absent_days, leave_days, remarks))
                
                conn.commit()
                log_action(session.get("user_id"), "record_attendance", "SUCCESS", 
                          f"Recorded attendance for student {sid} for month {attendance_month}")
                flash("Attendance recorded successfully!", "success")
                return redirect(url_for("index"))
            
            except Exception as e:
                conn.rollback()
                print(f"Error saving attendance: {e}")
                flash(f"Error saving attendance: {str(e)}", "error")
                return redirect(url_for("attendance", student_id=student_id))

        # Fetch attendance records for this student
        try:
            cur.execute("""
                SELECT id, student_id, TO_CHAR(attendance_month, 'Mon YYYY'), 
                       present_days, absent_days, leave_days,
                       CASE 
                           WHEN (present_days + absent_days) > 0 
                           THEN ROUND(present_days * 100.0 / (present_days + absent_days), 2)
                           ELSE 0
                       END AS percentage,
                       remarks
                FROM attendance_records 
                WHERE student_id = %s
                ORDER BY attendance_month DESC
            """, (sid,))
            
            attendance_records = cur.fetchall()
        except Exception as e:
            print(f"Error fetching records: {e}")
            attendance_records = []
        
        return render_template("attendance.html", student=student, 
                             attendance_records=attendance_records,
                             current_month=current_month)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        log_action(session.get("user_id"), "attendance", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("index"))

    finally:
        cur.close()
        conn.close()


@app.route("/scholarship/<student_id>", methods=["GET", "POST"])
def scholarship(student_id):
    if "user_email" not in session or session.get("role") != "admin":
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Convert student_id to proper format
        sid = str(student_id)
        cur.execute("SELECT * FROM students_data WHERE id = %s", (sid,))
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
            """, (sid, scholarship_type, amount, start_date, end_date, provider, status, remarks))

            conn.commit()
            log_action(session.get("user_id"), "add_scholarship", "SUCCESS", 
                      f"Added scholarship for student {sid}")
            flash("Scholarship saved successfully!", "success")
            return redirect(url_for("index"))

        cur.execute("""
            SELECT id, type, amount, start_date, end_date, provider, status 
            FROM scholarships 
            WHERE student_id = %s 
            ORDER BY start_date DESC
        """, (sid,))
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


@app.route("/documents/<student_id>", methods=["GET", "POST"])
def documents(student_id):
    if "user_email" not in session or session.get("role") != "admin":
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        sid = str(student_id)
        cur.execute("SELECT * FROM students_data WHERE id = %s", (sid,))
        student = cur.fetchone()

        if not student:
            flash("Student not found.", "error")
            return redirect(url_for("index"))

        documents = []

        if request.method == "POST":
            document_type = request.form.get("document_type")
            issue_date = request.form.get("issue_date") or None
            expiry_date = request.form.get("expiry_date") or None
            remarks = request.form.get("remarks", "").strip()
            file = request.files.get("document_file")

            # Validate inputs
            if not document_type or document_type == "":
                flash("Please select a document type.", "error")
                return redirect(url_for("documents", student_id=student_id))

            if not file or file.filename == "":
                flash("Please select a file to upload.", "error")
                return redirect(url_for("documents", student_id=student_id))

            # Validate file extension
            ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
            
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            
            if not allowed_file(file.filename):
                flash("Invalid file format. Allowed: PDF, JPG, PNG, DOC, DOCX", "error")
                return redirect(url_for("documents", student_id=student_id))

            try:
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join(os.getcwd(), 'uploads', 'documents')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate safe filename
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{sid}_{document_type}_{int(datetime.now().timestamp())}.{file_ext}"
                safe_filename = secure_filename(filename)
                file_path = os.path.join(upload_dir, safe_filename)
                
                # Save file
                file.save(file_path)
                
                # Save to database
                cur.execute("""
                    INSERT INTO student_documents (student_id, document_type, filename, file_path, issue_date, expiry_date, remarks)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (sid, document_type, safe_filename, file_path, issue_date, expiry_date, remarks))

                conn.commit()
                log_action(session.get("user_id"), "upload_document", "SUCCESS", 
                          f"Uploaded document {document_type} for student {sid}")
                flash("Document uploaded successfully!", "success")
                return redirect(url_for("documents", student_id=student_id))
                
            except Exception as file_error:
                conn.rollback()
                print(f"File upload error: {file_error}")
                flash(f"Error saving file: {str(file_error)}", "error")
                return redirect(url_for("documents", student_id=student_id))

        cur.execute("""
            SELECT id, document_type, created_at 
            FROM student_documents 
            WHERE student_id = %s 
            ORDER BY created_at DESC
        """, (sid,))
        documents = cur.fetchall()

        return render_template("student_documents.html", student=student, documents=documents)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        log_action(session.get("user_id"), "documents", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("index"))

    finally:
        cur.close()
        conn.close()


@app.route("/download-document/<int:doc_id>", methods=["GET"])
def download_document(doc_id):
    if "user_email" not in session or session.get("role") != "admin":
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT file_path, filename, document_type FROM student_documents WHERE id = %s
        """, (doc_id,))
        doc_record = cur.fetchone()

        if not doc_record:
            flash("Document not found.", "error")
            return redirect(url_for("index"))

        file_path = doc_record[0]
        filename = doc_record[1]

        if file_path and os.path.exists(file_path):
            log_action(session.get("user_id"), "download_document", "SUCCESS", 
                      f"Downloaded document {filename}")
            from flask import send_file
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            flash("File not found on server.", "error")
            return redirect(url_for("index"))

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "download_document", "ERROR", str(e))
        flash("Error downloading document.", "error")
        return redirect(url_for("index"))

    finally:
        cur.close()
        conn.close()


@app.route("/delete-document/<int:doc_id>", methods=["POST"])
def delete_document(doc_id):
    if "user_email" not in session or session.get("role") != "admin":
        return {"error": "Unauthorized"}, 403

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT file_path, student_id FROM student_documents WHERE id = %s
        """, (doc_id,))
        doc_record = cur.fetchone()

        if not doc_record:
            return {"error": "Document not found"}, 404

        file_path = doc_record[0]
        student_id = doc_record[1]

        # Delete file from disk if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as file_error:
                print(f"Error deleting file: {file_error}")

        # Delete from database
        cur.execute("DELETE FROM student_documents WHERE id = %s", (doc_id,))
        conn.commit()

        log_action(session.get("user_id"), "delete_document", "SUCCESS", 
                  f"Deleted document {doc_id}")
        flash("Document deleted successfully!", "success")
        return {"success": True}, 200

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        log_action(session.get("user_id"), "delete_document", "ERROR", str(e))
        return {"error": str(e)}, 500

    finally:
        cur.close()
        conn.close()
