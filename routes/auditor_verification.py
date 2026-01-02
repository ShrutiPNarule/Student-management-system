"""
Auditor Verification Route - Auditors review pending changes
"""
from flask import render_template, request, redirect, url_for, flash, session, abort, jsonify
from app import app
from db import get_connection
import json
from routes.log_utils import log_action
from datetime import datetime


@app.route("/auditor/pending-changes", methods=["GET"])
def auditor_pending_changes():
    """Display pending changes for auditor to verify"""
    
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "auditor":
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

        # Get pending changes
        cur.execute("""
            SELECT 
                pc.id, 
                pc.change_type, 
                pc.student_id, 
                pc.data, 
                pc.original_data,
                pc.created_by,
                u.name as created_by_name,
                pc.created_at,
                pc.status
            FROM pending_changes pc
            JOIN users_master u ON pc.created_by = u.id
            WHERE pc.status = 'pending'
            ORDER BY pc.created_at DESC
        """)

        raw_pending_list = cur.fetchall()
        
        # Parse JSONB data
        pending_list = []
        for row in raw_pending_list:
            row_list = list(row)
            # Parse data (index 3) and original_data (index 4)
            if row_list[3]:
                row_list[3] = json.loads(row_list[3]) if isinstance(row_list[3], str) else row_list[3]
            if row_list[4]:
                row_list[4] = json.loads(row_list[4]) if isinstance(row_list[4], str) else row_list[4]
            pending_list.append(tuple(row_list))

        cur.close()
        conn.close()

        return render_template(
            "auditor_verify_changes.html",
            pending_changes=pending_list,
            total_pending=len(pending_list)
        )

    except Exception as e:
        flash(f"Error loading pending changes: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/auditor/verify-change/<change_id>", methods=["POST"])
def auditor_verify_change(change_id):
    """Auditor verifies or rejects a pending change"""
    
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "auditor":
        abort(403)

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get current auditor info
        cur.execute(
            "SELECT id FROM users_master WHERE email = %s",
            (session.get("user_email"),)
        )
        auditor_result = cur.fetchone()
        if not auditor_result:
            flash("Auditor not found.", "error")
            return redirect(url_for("auditor_pending_changes"))

        auditor_id = auditor_result[0]

        # Get form data
        action = request.form.get("action")  # 'approve' or 'reject'
        remarks = request.form.get("remarks", "").strip()

        if action == "approve":
            # Mark as auditor_verified
            cur.execute("""
                UPDATE pending_changes
                SET status = 'auditor_verified',
                    auditor_id = %s,
                    auditor_verified_at = CURRENT_TIMESTAMP,
                    auditor_remarks = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (auditor_id, remarks, change_id))

            # Get the change details for logging
            cur.execute(
                "SELECT change_type, created_by FROM pending_changes WHERE id = %s",
                (change_id,)
            )
            change_data = cur.fetchone()
            
            # Log the action
            log_action(
                session.get("user_email"),
                "AUDITOR_VERIFIED",
                f"Verified change {change_id} of type {change_data[0]}",
                change_data[1]
            )

            conn.commit()
            flash("Change verified and forwarded to admin for approval.", "success")

        elif action == "reject":
            # Mark as rejected_by_auditor
            cur.execute("""
                UPDATE pending_changes
                SET status = 'rejected_by_auditor',
                    auditor_id = %s,
                    auditor_verified_at = CURRENT_TIMESTAMP,
                    auditor_remarks = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (auditor_id, remarks, change_id))

            # Get the change details for logging
            cur.execute(
                "SELECT change_type, created_by FROM pending_changes WHERE id = %s",
                (change_id,)
            )
            change_data = cur.fetchone()
            
            # Log the action
            log_action(
                session.get("user_email"),
                "AUDITOR_REJECTED",
                f"Rejected change {change_id}: {remarks}",
                change_data[1]
            )

            conn.commit()
            flash("Change rejected. The initiator will be notified.", "warning")

        else:
            flash("Invalid action.", "error")

        cur.close()
        conn.close()
        return redirect(url_for("auditor_pending_changes"))

    except Exception as e:
        flash(f"Error processing verification: {str(e)}", "error")
        if 'conn' in locals():
            conn.rollback()
        return redirect(url_for("auditor_pending_changes"))
