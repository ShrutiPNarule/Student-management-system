"""
Admin Approval Management Route
Superadmin reviews and approves/rejects admin requests to edit/delete student data
"""
from flask import render_template, request, redirect, url_for, flash, session, abort
from app import app
from db import get_connection
import psycopg2
import json
from routes.log_utils import log_action


@app.route("/approvals", methods=["GET"])
def view_approvals():
    """Superadmin views pending approval requests"""
    
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get all pending requests
        cur.execute("""
            SELECT 
                ar.id,
                ar.request_type,
                ar.entity_type,
                ar.entity_id,
                ar.action_data,
                ar.status,
                ar.created_at,
                u.name as admin_name,
                u.email as admin_email,
                ar.admin_id
            FROM admin_approval_requests ar
            JOIN users_master u ON ar.admin_id = u.id
            WHERE ar.status = 'pending'
            ORDER BY ar.created_at DESC
        """)
        
        requests = cur.fetchall()
        cur.close()
        
        return render_template("approvals.html", requests=requests)

    except psycopg2.Error as e:
        print(f"[APPROVALS ERROR] {e}")
        flash("Database error occurred.", "error")
        cur.close()
        return redirect(url_for("index"))


@app.route("/approve/<request_id>", methods=["POST"])
def approve_request(request_id):
    """Superadmin approves a request"""
    
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        abort(403)

    approval_notes = request.form.get("notes", "").strip()
    
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get request details
        cur.execute("""
            SELECT 
                request_type, entity_type, entity_id, action_data, admin_id
            FROM admin_approval_requests
            WHERE id = %s AND status = 'pending'
        """, (request_id,))
        
        req_data = cur.fetchone()
        if not req_data:
            flash("Request not found or already processed.", "error")
            cur.close()
            return redirect(url_for("view_approvals"))
        
        request_type, entity_type, entity_id, action_data, admin_id = req_data
        
        # Get current user ID
        cur.execute("SELECT id FROM users_master WHERE email = %s", (session["user_email"],))
        superadmin_id = cur.fetchone()[0]
        
        # Process based on request type
        if request_type == "DELETE":
            # Soft delete student
            cur.execute("""
                UPDATE students_master
                SET is_deleted = TRUE
                WHERE id = %s AND is_deleted = FALSE
            """, (entity_id,))

            # Soft delete related marks
            cur.execute("""
                UPDATE student_marks
                SET is_deleted = TRUE
                WHERE student_id = %s
            """, (entity_id,))
            
            action_msg = "APPROVED DELETE"
            
        elif request_type == "EDIT":
            # Apply the changes from action_data
            if isinstance(action_data, str):
                data = json.loads(action_data)
            else:
                data = action_data
            
            print(f"[APPROVAL] Processing EDIT for student {entity_id}")
            print(f"[APPROVAL] Action data: {data}")
            
            # Get user_id from students_master
            cur.execute("SELECT user_id FROM students_master WHERE id = %s", (entity_id,))
            user_result = cur.fetchone()
            if not user_result:
                flash("Student record not found.", "error")
                cur.close()
                return redirect(url_for("view_approvals"))
            
            user_id = user_result[0]
            
            # Build dynamic UPDATE for users_master based on provided fields
            user_updates = []
            user_params = []
            # User fields: name, email, phone, address, dob, birth_place, category
            user_fields = ["name", "email", "phone", "dob", "birth_place", "category"]
            for field in user_fields:
                if field in data and data[field] is not None:
                    user_updates.append(f"{field} = %s")
                    user_params.append(data[field])
            
            if user_updates:
                user_params.append(user_id)
                update_query = f"UPDATE users_master SET {', '.join(user_updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s"
                print(f"[APPROVAL] Users update query: {update_query} | Params: {user_params}")
                cur.execute(update_query, user_params)
            
            # Build dynamic UPDATE for students_master based on provided fields
            student_updates = []
            student_params = []
            student_fields = ["enrollment_no", "current_status"]
            for field in student_fields:
                if field in data and data[field] is not None:
                    student_updates.append(f"{field} = %s")
                    student_params.append(data[field])
            
            if student_updates:
                student_params.append(entity_id)
                update_query = f"UPDATE students_master SET {', '.join(student_updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s AND is_deleted = FALSE"
                print(f"[APPROVAL] Student update query: {update_query} | Params: {student_params}")
                cur.execute(update_query, student_params)
            
            # Handle college update (create/update college_enrollment if college is provided)
            if "college" in data and data["college"] is not None:
                print(f"[APPROVAL] Processing college update: {data['college']}")
                # First, try to find college by name
                cur.execute("""
                    SELECT id FROM colleges_master WHERE name ILIKE %s LIMIT 1
                """, (data["college"],))
                college_result = cur.fetchone()
                
                if college_result:
                    college_id = college_result[0]
                    # Check if enrollment exists
                    cur.execute("""
                        SELECT id FROM college_enrollment 
                        WHERE student_id = %s
                    """, (entity_id,))
                    
                    if cur.fetchone():
                        # Update existing enrollment
                        cur.execute("""
                            UPDATE college_enrollment 
                            SET college_id = %s, updated_at = CURRENT_TIMESTAMP
                            WHERE student_id = %s
                        """, (college_id, entity_id))
                    else:
                        # Create new enrollment
                        cur.execute("""
                            INSERT INTO college_enrollment (student_id, college_id, status)
                            VALUES (%s, %s, 'Active')
                        """, (entity_id, college_id))
                    print(f"[APPROVAL] College enrollment updated to: {data['college']}")
            
            
            # Build dynamic UPDATE for student_marks based on provided fields
            marks_updates = []
            marks_params = []
            marks_fields = ["marks_10th", "marks_12th", "marks1", "marks2", "marks3", "marks4", "marks5", "marks6", "marks7", "marks8"]
            for field in marks_fields:
                if field in data and data[field] is not None:
                    marks_updates.append(f"{field} = %s")
                    marks_params.append(data[field])
            
            if marks_updates:
                # First check if student_marks record exists
                cur.execute("SELECT id FROM student_marks WHERE student_id = %s", (entity_id,))
                marks_record = cur.fetchone()
                
                if marks_record:
                    # Update existing record
                    marks_params.append(entity_id)
                    update_query = f"UPDATE student_marks SET {', '.join(marks_updates)}, updated_at = CURRENT_TIMESTAMP WHERE student_id = %s"
                    print(f"[APPROVAL] Marks update query: {update_query} | Params: {marks_params}")
                    cur.execute(update_query, marks_params)
                else:
                    # Insert new record
                    insert_fields = ["student_id"]
                    insert_values = [entity_id]
                    insert_placeholders = ["%s"]
                    
                    # Add marks fields to insert
                    marks_data = {}
                    for field in marks_fields:
                        if field in data and data[field] is not None:
                            marks_data[field] = data[field]
                        else:
                            marks_data[field] = 0
                    
                    for field in marks_fields:
                        insert_fields.append(field)
                        insert_values.append(marks_data[field])
                        insert_placeholders.append("%s")
                    
                    insert_query = f"INSERT INTO student_marks ({', '.join(insert_fields)}) VALUES ({', '.join(insert_placeholders)})"
                    print(f"[APPROVAL] Marks insert query: {insert_query} | Params: {insert_values}")
                    cur.execute(insert_query, insert_values)
            
            print(f"[APPROVAL] EDIT approval completed for student {entity_id}")
            action_msg = "APPROVED EDIT"
        
        # Update request status
        cur.execute("""
            UPDATE admin_approval_requests
            SET status = 'approved',
                approved_by = %s,
                approval_notes = %s,
                approved_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (superadmin_id, approval_notes, request_id))
        
        conn.commit()
        
        # Log action
        log_action(action_msg, entity_type, entity_id, {
            "requested_by": admin_id,
            "approved_by": superadmin_id,
            "notes": approval_notes
        })
        
        flash(f"Request {request_type.lower()} approved successfully!", "success")
        
    except Exception as e:
        conn.rollback()
        print(f"[APPROVAL ERROR] {e}")
        flash("Error processing approval.", "error")
    
    finally:
        cur.close()
    
    return redirect(url_for("view_approvals"))


@app.route("/reject/<request_id>", methods=["POST"])
def reject_request(request_id):
    """Superadmin rejects a request"""
    
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        abort(403)

    rejection_reason = request.form.get("notes", "").strip()
    
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get request details
        cur.execute("""
            SELECT request_type FROM admin_approval_requests
            WHERE id = %s AND status = 'pending'
        """, (request_id,))
        
        req_data = cur.fetchone()
        if not req_data:
            flash("Request not found or already processed.", "error")
            cur.close()
            return redirect(url_for("view_approvals"))
        
        # Get current user ID
        cur.execute("SELECT id FROM users_master WHERE email = %s", (session["user_email"],))
        superadmin_id = cur.fetchone()[0]
        
        # Update request status
        cur.execute("""
            UPDATE admin_approval_requests
            SET status = 'rejected',
                approved_by = %s,
                approval_notes = %s,
                approved_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (superadmin_id, rejection_reason, request_id))
        
        conn.commit()
        
        flash("Request rejected successfully!", "success")
        
    except Exception as e:
        conn.rollback()
        print(f"[REJECTION ERROR] {e}")
        flash("Error rejecting request.", "error")
    
    finally:
        cur.close()
    
    return redirect(url_for("view_approvals"))
