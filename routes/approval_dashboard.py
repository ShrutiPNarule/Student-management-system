from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app import app
from db import get_connection
from routes.log_utils import log_action
from datetime import datetime, timedelta


@app.route("/approval-dashboard", methods=["GET"])
def approval_dashboard():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    if session.get("role") != "superadmin":
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    approvals = []

    try:
        filter_status = request.args.get("filter_status", "")
        filter_type = request.args.get("filter_type", "")
        from_date = request.args.get("from_date", "")
        to_date = request.args.get("to_date", "")

        query = "SELECT id, student_id, type, student_name, requested_by, created_at, status FROM approval_requests WHERE 1=1"
        params = []

        if filter_status:
            query += " AND status = %s"
            params.append(filter_status)

        if filter_type:
            query += " AND type = %s"
            params.append(filter_type)

        if from_date:
            query += " AND created_at >= %s"
            params.append(from_date)

        if to_date:
            query += " AND created_at <= %s"
            params.append(to_date + " 23:59:59")

        query += " ORDER BY created_at DESC"
        cur.execute(query, params)
        approvals = cur.fetchall()

        log_action(session.get("user_id"), "view_approval_dashboard", "SUCCESS", f"Viewed {len(approvals)} approvals")

    except Exception as e:
        print(f"Error: {e}")
        log_action(session.get("user_id"), "view_approval_dashboard", "ERROR", str(e))
        flash("An error occurred.", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("approval_dashboard.html", approvals=approvals)


@app.route("/bulk-approval", methods=["GET", "POST"])
def bulk_approval():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    user_role = session.get("role")
    if user_role not in ["admin", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        try:
            request_ids = request.form.getlist("request_ids")
            approval_notes = request.form.get("approval_notes", "")

            if not request_ids:
                flash("No requests selected.", "error")
                return redirect(url_for("bulk_approval"))

            approved_count = 0
            for req_id in request_ids:
                cur.execute("""
                    UPDATE admin_approval_requests 
                    SET status = 'approved', approved_by = %s, approval_notes = %s, approved_at = NOW()
                    WHERE id = %s
                """, (session.get("user_email"), approval_notes, req_id))
                approved_count += 1

            conn.commit()
            log_action(session.get("user_id"), "bulk_approval", "SUCCESS", f"Approved {approved_count} requests")
            flash(f"Successfully approved {approved_count} requests.", "success")
            return redirect(url_for("approval_dashboard"))

        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            log_action(session.get("user_id"), "bulk_approval", "ERROR", str(e))
            flash("An error occurred during bulk approval.", "error")
            return redirect(url_for("bulk_approval"))

        finally:
            cur.close()
            conn.close()

    # GET method
    try:
        cur.execute("""
            SELECT 
                ar.id, 
                ar.request_type,
                ar.request_type,
                COALESCE(u_student.name, 'N/A') as student_name, 
                COALESCE(u_admin.email, 'N/A') as requested_by, 
                ar.created_at 
            FROM admin_approval_requests ar
            LEFT JOIN students_master s ON ar.entity_id = s.id
            LEFT JOIN users_master u_student ON s.user_id = u_student.id
            LEFT JOIN users_master u_admin ON ar.admin_id = u_admin.id
            WHERE ar.status = 'pending' 
            ORDER BY ar.created_at DESC
        """)
        pending_requests = cur.fetchall()
        print(f"Pending requests fetched: {len(pending_requests)}")

    except Exception as e:
        print(f"Error fetching pending requests: {e}")
        log_action(session.get("user_id"), "bulk_approval_fetch", "ERROR", str(e))
        flash(f"Error fetching requests: {str(e)}", "error")
        pending_requests = []

    finally:
        cur.close()
        conn.close()

    return render_template("bulk_approval.html", pending_requests=pending_requests)


@app.route("/request-timeline", methods=["GET"])
def request_timeline():
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    user_role = session.get("role")
    if user_role not in ["admin", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))

    conn = get_connection()
    cur = conn.cursor()
    requests_list = []

    try:
        from_date = request.args.get("from_date", "").strip()
        to_date = request.args.get("to_date", "").strip()
        status = request.args.get("status", "").strip()
        req_type = request.args.get("type", "").strip()

        query = """
            SELECT 
                ar.id, 
                ar.entity_id,
                ar.request_type, 
                u_student.name as student_name, 
                u_admin.email as requested_by, 
                ar.created_at, 
                ar.status 
            FROM admin_approval_requests ar
            LEFT JOIN students_master s ON ar.entity_id = s.id
            LEFT JOIN users_master u_student ON s.user_id = u_student.id
            LEFT JOIN users_master u_admin ON ar.admin_id = u_admin.id
            WHERE 1=1
        """
        params = []

        if from_date:
            query += " AND DATE(ar.created_at) >= %s"
            params.append(from_date)

        if to_date:
            query += " AND DATE(ar.created_at) <= %s"
            params.append(to_date)

        if status and status != "":
            query += " AND ar.status = %s"
            params.append(status)

        if req_type and req_type != "":
            query += " AND ar.request_type = %s"
            params.append(req_type)

        query += " ORDER BY ar.created_at DESC"
        
        print(f"Query: {query}")
        print(f"Params: {params}")
        
        cur.execute(query, params)
        requests_list = cur.fetchall()

        log_action(session.get("user_id"), "view_request_timeline", "SUCCESS", f"Viewed {len(requests_list)} requests")

    except Exception as e:
        print(f"Error in request_timeline: {e}")
        log_action(session.get("user_id"), "view_request_timeline", "ERROR", str(e))
        flash(f"An error occurred: {str(e)}", "error")

    finally:
        cur.close()
        conn.close()

    return render_template("request_timeline.html", requests=requests_list)
