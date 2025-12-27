from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
from routes.log_utils import log_action
import csv
from io import StringIO


@app.route("/bulk-upload-students", methods=["GET", "POST"])
def bulk_upload_students():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        flash("Only admins can upload students.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            file = request.files.get("csv_file")
            if not file or file.filename == "":
                flash("No file selected.", "error")
                return redirect(url_for("bulk_upload_students"))

            encoding = request.form.get("encoding", "utf-8")
            skip_duplicates = request.form.get("skip_duplicates") == "on"

            conn = get_connection()
            cur = conn.cursor()

            stream = StringIO(file.stream.read().decode(encoding))
            reader = csv.DictReader(stream)

            uploaded_count = 0
            skipped_count = 0
            error_count = 0

            for idx, row in enumerate(reader, 1):
                try:
                    if idx > 1000:
                        flash("Maximum 1000 students per upload exceeded.", "error")
                        break

                    email = row.get("email", "").lower().strip()

                    if skip_duplicates:
                        cur.execute("SELECT id FROM students_data WHERE email = %s", (email,))
                        if cur.fetchone():
                            skipped_count += 1
                            continue

                    cur.execute("""
                        INSERT INTO students_data 
                        (name, roll_no, phone, email, college, marks_10th, marks_12th, 
                         marks_year1, marks_year2, marks_year3, gpa, dob, birth_place, 
                         religion, category, caste)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row.get("name"), row.get("roll_no"), row.get("phone"), email,
                        row.get("college"), float(row.get("marks_10th", 0)), float(row.get("marks_12th", 0)),
                        float(row.get("marks_year1", 0)), float(row.get("marks_year2", 0)), 
                        float(row.get("marks_year3", 0)), float(row.get("gpa", 0)),
                        row.get("dob"), row.get("birth_place"), row.get("religion"), 
                        row.get("category"), row.get("caste")
                    ))
                    uploaded_count += 1

                except Exception as e:
                    error_count += 1
                    print(f"Row {idx} error: {e}")
                    continue

            conn.commit()
            cur.close()
            conn.close()

            log_action(session.get("user_id"), "bulk_upload_students", "SUCCESS", 
                      f"Uploaded: {uploaded_count}, Skipped: {skipped_count}, Errors: {error_count}")
            
            flash(f"Upload complete! Added: {uploaded_count}, Skipped: {skipped_count}, Errors: {error_count}", "success")
            return redirect(url_for("index"))

        except Exception as e:
            print(f"Error: {e}")
            log_action(session.get("user_id"), "bulk_upload_students", "ERROR", str(e))
            flash("An error occurred during upload.", "error")
            return redirect(url_for("bulk_upload_students"))

    return render_template("bulk_upload_students.html")


@app.route("/download-csv-template")
def download_csv_template():
    if "user_email" not in session or session.get("role") != "admin":
        flash("Unauthorized.", "error")
        return redirect(url_for("index"))

    csv_content = """name,roll_no,phone,email,college,marks_10th,marks_12th,marks_year1,marks_year2,marks_year3,gpa,dob,birth_place,religion,category,caste
Student Name,ROLL001,9876543210,student@example.com,XYZ College,85.5,88.0,80.0,82.0,85.0,8.0,2000-01-15,City,Hindu,General,
"""
    
    response = app.make_response(csv_content)
    response.headers["Content-Disposition"] = "attachment; filename=student_template.csv"
    response.headers["Content-Type"] = "text/csv"
    return response
