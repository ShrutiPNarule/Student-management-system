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
            
            # Get user_id from students_master
            cur.execute("SELECT user_id FROM students_master WHERE id = %s", (entity_id,))
            user_result = cur.fetchone()
            if not user_result:
                flash("Student record not found.", "error")
                cur.close()
                return redirect(url_for("view_approvals"))
            
            user_id = user_result[0]
            
            # Update users_master (name, email, phone, address/college)
            cur.execute("""
                UPDATE users_master
                SET name = %s,
                    email = %s,
                    phone = %s,
                    address = %s
                WHERE id = %s
            """, (
                data.get("name"),
                data.get("email"),
                data.get("phone"),
                data.get("college"),
                user_id
            ))
            
            # Update students_master (enrollment_no, college)
            cur.execute("""
                UPDATE students_master
                SET enrollment_no = %s
                WHERE id = %s AND is_deleted = FALSE
            """, (
                data.get("enrollment_no"),
                entity_id
            ))
            
            # Update student_marks if marks data provided
            if any(k in data for k in ["marks_10th", "marks_12th", "marks1", "marks2", "marks3", "marks4"]):
                cur.execute("""
                    UPDATE student_marks
                    SET marks_10th = COALESCE(%s, marks_10th),
                        marks_12th = COALESCE(%s, marks_12th),
                        marks1 = COALESCE(%s, marks1),
                        marks2 = COALESCE(%s, marks2),
                        marks3 = COALESCE(%s, marks3),
                        marks4 = COALESCE(%s, marks4)
                    WHERE student_id = %s
                """, (
                    data.get("marks_10th"),
                    data.get("marks_12th"),
                    data.get("marks1"),
                    data.get("marks2"),
                    data.get("marks3"),
                    data.get("marks4"),
                    entity_id
                ))
            
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
