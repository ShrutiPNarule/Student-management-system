from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
from werkzeug.security import check_password_hash, generate_password_hash
import re
from routes.log_utils import log_action


PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,128}$'


@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        current_password = request.form.get("current_password", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        # ---------- VALIDATION ----------
        if not current_password or not new_password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for("change_password"))

        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return redirect(url_for("change_password"))

        if not re.match(PASSWORD_REGEX, new_password):
            flash("Password must contain uppercase, lowercase, number, and special character (@$!%*?&).", "error")
            return redirect(url_for("change_password"))

        try:
            # ---------- FETCH USER ----------
            cur.execute("SELECT password_hash FROM users_master WHERE email = %s", (session["user_email"],))
            user = cur.fetchone()

            if not user:
                flash("User not found.", "error")
                return redirect(url_for("change_password"))

            # ---------- VERIFY CURRENT PASSWORD ----------
            if not check_password_hash(user[0], current_password):
                log_action(session.get("user_id"), "change_password", "FAILURE", "Incorrect current password")
                flash("Current password is incorrect.", "error")
                return redirect(url_for("change_password"))

            # ---------- UPDATE PASSWORD ----------
            new_password_hash = generate_password_hash(new_password)
            cur.execute(
                "UPDATE users_master SET password_hash = %s, updated_at = NOW() WHERE email = %s",
                (new_password_hash, session["user_email"])
            )
            conn.commit()

            log_action(session.get("user_id"), "change_password", "SUCCESS", "Password changed successfully")
            flash("Password changed successfully! Please login again.", "success")
            return redirect(url_for("logout"))

        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            log_action(session.get("user_id"), "change_password", "ERROR", str(e))
            flash("An error occurred while changing password.", "error")
            return redirect(url_for("change_password"))

        finally:
            cur.close()
            conn.close()

    return render_template("change_password.html")
