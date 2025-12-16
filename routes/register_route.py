from flask import render_template, request, redirect, url_for, flash
from app import app
from db import get_connection
from werkzeug.security import generate_password_hash
import psycopg2
import re

# ------------ REGISTER (CREATE ACCOUNT) ------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("register.html")

        # Password strength checks
        if (
            len(password) < 8
            or not re.search(r"[A-Z]", password)
            or not re.search(r"[a-z]", password)
            or not re.search(r"[0-9]", password)
            or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
        ):
            flash(
                "Password must be at least 8 characters long and include uppercase, "
                "lowercase, number, and special character.",
                "error",
            )
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(
            password,
            method="pbkdf2:sha256",
            salt_length=16,
        )
        print("REGISTER DEBUG hashed:", hashed_password)

        conn = None
        cur = None
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Get role_id for 'student'
            cur.execute(
                "SELECT id FROM roles_master WHERE name = %s",
                ("student",),
            )
            row = cur.fetchone()
            if not row:
                flash("Role 'student' not found in roles table.", "error")
                return render_template("register.html")

            student_role_id = row[0]

            # Store hashed_password in DB with default role = student
            cur.execute(
                """
                INSERT INTO users_master (email, password, role_id)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (email, hashed_password, student_role_id),
            )
            conn.commit()

            flash("Account created successfully. Please login.", "success")
            return redirect(url_for("login"))

        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print("REGISTER ERROR:", e)
            # Most common error = duplicate email
            flash("This email is already registered or there was a database error.", "error")
            return render_template("register.html")

        finally:
            if cur:
                cur.close()

    # GET
    return render_template("register.html")
