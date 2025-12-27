from flask import render_template, request, redirect, url_for, flash, session
from app import app
from db import get_connection
import pyotp
import qrcode
from io import BytesIO
import base64
from routes.log_utils import log_action


@app.route("/2fa/setup", methods=["GET", "POST"])
def setup_2fa():
    # ---------- AUTH CHECK ----------
    if "user_email" not in session:
        flash("Please login to continue.", "error")
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        verification_code = request.form.get("verification_code", "").strip()
        backup_confirm = request.form.get("backup_confirm")
        secret_key = request.form.get("secret_key", "").strip()

        # ---------- VALIDATION ----------
        if not verification_code or not backup_confirm or not secret_key:
            flash("All fields are required.", "error")
            return redirect(url_for("setup_2fa"))

        if len(verification_code) != 6 or not verification_code.isdigit():
            flash("Verification code must be 6 digits.", "error")
            return redirect(url_for("setup_2fa"))

        try:
            # ---------- VERIFY OTP ----------
            totp = pyotp.TOTP(secret_key)
            if not totp.verify(verification_code):
                log_action(session.get("user_id"), "2fa_setup", "FAILURE", "Invalid verification code")
                flash("Invalid verification code. Please try again.", "error")
                return redirect(url_for("setup_2fa"))

            # ---------- GENERATE BACKUP CODES ----------
            backup_codes = [pyotp.random_base32()[:8].upper() for _ in range(10)]

            # ---------- UPDATE USER ----------
            cur.execute(
                """UPDATE users_master 
                   SET two_factor_enabled = true, two_factor_secret = %s, 
                       backup_codes = %s, updated_at = NOW()
                   WHERE email = %s""",
                (secret_key, ','.join(backup_codes), session["user_email"])
            )
            conn.commit()

            log_action(session.get("user_id"), "2fa_setup", "SUCCESS", "2FA enabled successfully")
            flash("Two-Factor Authentication enabled successfully! Save your backup codes.", "success")
            return redirect(url_for("index"))

        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
            log_action(session.get("user_id"), "2fa_setup", "ERROR", str(e))
            flash("An error occurred while setting up 2FA.", "error")
            return redirect(url_for("setup_2fa"))

        finally:
            cur.close()
            conn.close()

    # ---------- GET METHOD: Generate new secret & QR Code ----------
    try:
        cur.execute("SELECT email FROM users_master WHERE email = %s", (session["user_email"],))
        user = cur.fetchone()

        if user:
            # Generate secret key
            secret_key = pyotp.random_base32()
            
            # Generate QR Code
            totp = pyotp.TOTP(secret_key)
            qr_uri = totp.provisioning_uri(name=user[0], issuer_name="Student Management System")
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            qr_base64 = base64.b64encode(img_io.getvalue()).decode()
            qr_image = f"data:image/png;base64,{qr_base64}"

            return render_template("setup_2fa.html", qr_image=qr_image, secret_key=secret_key)
        else:
            flash("User not found.", "error")
            return redirect(url_for("index"))

    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred while generating 2FA setup.", "error")
        return redirect(url_for("index"))

    finally:
        cur.close()
        conn.close()
