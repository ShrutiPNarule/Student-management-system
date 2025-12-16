from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
import psycopg2
from routes import require_roles
from routes.log_utils import log_action

@app.route("/delete-account", methods=["GET", "POST"])
@require_roles("general")   # Only general users can remove themselves
def remove_logged_account():

    if request.method == "POST":
        email = session.get("user_email")

        try:
            conn = get_connection()
            cur = conn.cursor()

            # Soft delete instead of permanent delete
            cur.execute("""
                UPDATE users
                SET is_deleted = TRUE
                WHERE email = %s
            """, (email,))

            conn.commit()

            # Log action
            log_action("ACCOUNT_DELETE", f"Account deleted for email={email}")

            # Clear session
            session.clear()
            flash("Your account has been deleted successfully.", "success")
            return redirect(url_for("login"))

        except psycopg2.Error as e:
            conn.rollback()
            print("DELETE ACCOUNT ERROR:", e)
            flash("Could not delete account. Please try again.", "error")
            return redirect(url_for("remove_logged_account"))

        finally:
            cur.close()
            conn.close()

    return render_template("delete_account.html")
