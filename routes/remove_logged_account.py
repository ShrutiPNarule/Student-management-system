from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
import psycopg2
from routes.log_utils import log_action

@app.route("/delete-account", methods=["GET", "POST"])
def remove_logged_account():

    if request.method == "POST":
        user_id = session.get("user_id")
        email = session.get("user_email")

        try:
            conn = get_connection()
            cur = conn.cursor()

            # Delete the user account
            cur.execute("""
                DELETE FROM users_master
                WHERE id = %s
            """, (user_id,))

            conn.commit()

            # Log action
            log_action("ACCOUNT_DELETE", "USER", user_id)

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

    return render_template("delete_account.html")
