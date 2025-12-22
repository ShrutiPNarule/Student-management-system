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
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        dob = request.form.get("dob", "").strip() or None
        address = request.form.get("address", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # ---------- BASIC VALIDATION ----------
        if not email or not password or not name:
            flash("Name, email, and password are required.", "error")
            return render_template("register.html")

        if not re.fullmatch(r"[A-Za-z\s]{2,}", name):
            flash("Name must contain only letters.", "error")
            return render_template("register.html")

        if phone and (not phone.isdigit() or len(phone) != 10):
            flash("Phone number must be exactly 10 digits.", "error")
            return render_template("register.html")

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            flash("Enter a valid email address.", "error")
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

            # Store all user details in DB with default role = student
            cur.execute(
                """
                INSERT INTO users_master (name, email, password, phone, role_id, dob, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (name, email, hashed_password, phone, student_role_id, dob, address),
            )
            user_id = cur.fetchone()[0]

            # Create student_master record for the user
            cur.execute(
                """
                INSERT INTO students_master (user_id, current_status)
                VALUES (%s, %s)
                """,
                (user_id, "active"),
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
