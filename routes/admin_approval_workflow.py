"""
Admin Approval Route - Admin reviews auditor-verified changes and applies them
"""
from flask import render_template, request, redirect, url_for, flash, session, abort
from app import app
from db import get_connection
import json
from routes.log_utils import log_action
from werkzeug.security import generate_password_hash
from datetime import datetime


@app.route("/admin/pending-approvals", methods=["GET"])
def admin_pending_approvals():
    """Display changes verified by auditor for admin approval"""
    
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get current user info
        cur.execute(
            "SELECT id FROM users_master WHERE email = %s",
            (session.get("user_email"),)
        )
        user_result = cur.fetchone()
        if not user_result:
            flash("User not found.", "error")
            return redirect(url_for("index"))

        current_user_id = user_result[0]

        # Get auditor-verified changes
        cur.execute("""
            SELECT 
                pc.id, 
                pc.change_type, 
                pc.student_id, 
                pc.data, 
                pc.original_data,
                pc.created_by,
                cu.name as created_by_name,
                pc.auditor_id,
                au.name as auditor_name,
                pc.auditor_verified_at,
                pc.auditor_remarks,
                pc.created_at
            FROM pending_changes pc
            JOIN users_master cu ON pc.created_by = cu.id
            JOIN users_master au ON pc.auditor_id = au.id
            WHERE pc.status = 'auditor_verified'
            ORDER BY pc.auditor_verified_at DESC
        """)

        auditor_verified_list = cur.fetchall()

        # Also get rejected items for reference
        cur.execute("""
            SELECT 
                pc.id, 
                pc.change_type, 
                pc.student_id, 
                pc.created_by,
                u.name as created_by_name,
                pc.status,
                pc.auditor_remarks,
                pc.admin_remarks
            FROM pending_changes pc
            JOIN users_master u ON pc.created_by = u.id
            WHERE pc.status IN ('rejected_by_auditor', 'rejected_by_admin')
            ORDER BY pc.updated_at DESC
            LIMIT 20
        """)

        rejected_list = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "admin_approve_changes.html",
            auditor_verified=auditor_verified_list,
            rejected=rejected_list,
            total_pending=len(auditor_verified_list)
        )

    except Exception as e:
        flash(f"Error loading approvals: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/admin/approve-change/<change_id>", methods=["POST"])
def admin_approve_change(change_id):
    """Admin approves auditor-verified change and applies it to main data"""
    
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get current admin info
        cur.execute(
            "SELECT id FROM users_master WHERE email = %s",
            (session.get("user_email"),)
        )
        admin_result = cur.fetchone()
        if not admin_result:
            flash("Admin not found.", "error")
            return redirect(url_for("admin_pending_approvals"))

        admin_id = admin_result[0]

        # Get form data
        action = request.form.get("action")  # 'approve' or 'reject'
        remarks = request.form.get("remarks", "").strip()

        # Get the pending change details
        cur.execute("""
            SELECT 
                id, 
                change_type, 
                student_id, 
                data, 
                created_by
            FROM pending_changes
            WHERE id = %s AND status = 'auditor_verified'
        """, (change_id,))

        change_result = cur.fetchone()
        if not change_result:
            flash("Change not found or already processed.", "error")
            return redirect(url_for("admin_pending_approvals"))

        pc_id, change_type, student_id, change_data_str, created_by = change_result
        change_data = json.loads(change_data_str)

        if action == "approve":
            # Apply the change based on type
            if change_type == "add_student":
                # Insert new student
                name = change_data.get("name")
                email = change_data.get("email")
                phone = change_data.get("phone")
                college = change_data.get("college")
                dob = change_data.get("dob")
                category = change_data.get("category")
                birth_place = change_data.get("birth_place")
                roll_no = change_data.get("roll_no")
                marks_data = change_data.get("marks", {})

                # Get student role
                cur.execute(
                    "SELECT id FROM roles_master WHERE name = %s",
                    ("student",)
                )
                role_row = cur.fetchone()
                student_role_id = role_row[0] if role_row else None

                # Create user
                cur.execute("""
                    INSERT INTO users_master (name, email, password, phone, role_id, address, dob, category, birth_place)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    name,
                    email,
                    generate_password_hash(email + roll_no, method="pbkdf2:sha256", salt_length=16),
                    phone,
                    student_role_id,
                    college,
                    dob,
                    category,
                    birth_place
                ))
                new_user_id = cur.fetchone()[0]

                # Create student record
                cur.execute("""
                    INSERT INTO students_master (user_id, enrollment_no, current_status)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (new_user_id, roll_no, "active"))
                new_student_id = cur.fetchone()[0]

                # Add marks
                if marks_data:
                    cur.execute("""
                        INSERT INTO student_marks 
                        (student_id, marks_10th, marks_12th, marks1, marks2, marks3, marks4, marks5, marks6, marks7, marks8)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        new_student_id,
                        marks_data.get("marks_10th", 0),
                        marks_data.get("marks_12th", 0),
                        marks_data.get("marks1", 0),
                        marks_data.get("marks2", 0),
                        marks_data.get("marks3", 0),
                        marks_data.get("marks4", 0),
                        marks_data.get("marks5", 0),
                        marks_data.get("marks6", 0),
                        marks_data.get("marks7", 0),
                        marks_data.get("marks8", 0)
                    ))

            elif change_type == "edit_student":
                # Update existing student
                marks_data = change_data.get("marks", {})
                
                cur.execute("""
                    SELECT user_id FROM students_master WHERE id = %s
                """, (student_id,))
                user_id_result = cur.fetchone()
                if user_id_result:
                    user_id = user_id_result[0]
                    cur.execute("""
                        UPDATE users_master
                        SET name = %s,
                            phone = %s,
                            address = %s,
                            dob = %s,
                            category = %s,
                            birth_place = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (
                        change_data.get("name"),
                        change_data.get("phone"),
                        change_data.get("college"),
                        change_data.get("dob"),
                        change_data.get("category"),
                        change_data.get("birth_place"),
                        user_id
                    ))

                    # Update marks
                    if marks_data:
                        cur.execute("""
                            UPDATE student_marks
                            SET marks_10th = %s,
                                marks_12th = %s,
                                marks1 = %s,
                                marks2 = %s,
                                marks3 = %s,
                                marks4 = %s,
                                marks5 = %s,
                                marks6 = %s,
                                marks7 = %s,
                                marks8 = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE student_id = %s
                        """, (
                            marks_data.get("marks_10th", 0),
                            marks_data.get("marks_12th", 0),
                            marks_data.get("marks1", 0),
                            marks_data.get("marks2", 0),
                            marks_data.get("marks3", 0),
                            marks_data.get("marks4", 0),
                            marks_data.get("marks5", 0),
                            marks_data.get("marks6", 0),
                            marks_data.get("marks7", 0),
                            marks_data.get("marks8", 0),
                            student_id
                        ))

            # Mark change as completed
            cur.execute("""
                UPDATE pending_changes
                SET status = 'admin_approved',
                    admin_id = %s,
                    admin_approved_at = CURRENT_TIMESTAMP,
                    admin_remarks = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (admin_id, remarks, change_id))

            # Log the action
            log_action(
                session.get("user_email"),
                "ADMIN_APPROVED",
                f"Approved and applied change {change_id} of type {change_type}",
                created_by
            )

            conn.commit()
            flash("Change approved and applied to system.", "success")

        elif action == "reject":
            # Mark as rejected_by_admin
            cur.execute("""
                UPDATE pending_changes
                SET status = 'rejected_by_admin',
                    admin_id = %s,
                    admin_approved_at = CURRENT_TIMESTAMP,
                    admin_remarks = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (admin_id, remarks, change_id))

            # Log the action
            log_action(
                session.get("user_email"),
                "ADMIN_REJECTED",
                f"Rejected change {change_id}: {remarks}",
                created_by
            )

            conn.commit()
            flash("Change rejected. The initiator will be notified.", "warning")

        else:
            flash("Invalid action.", "error")

        cur.close()
        conn.close()
        return redirect(url_for("admin_pending_approvals"))

    except Exception as e:
        flash(f"Error processing approval: {str(e)}", "error")
        if 'conn' in locals():
            conn.rollback()
        return redirect(url_for("admin_pending_approvals"))
