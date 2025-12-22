import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------ EMAIL CONFIG (CHANGE THIS!) ------------

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "academic.techwork@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "urjwuasqzoirpxot")


def send_otp_email(to_email, otp):
    """✅ TC_LOGIN_044: Send OTP email"""
    subject = "Your Login OTP"
    body = f"""
    Your OTP for login is: {otp}
    
    This OTP is valid for 5 minutes.
    
    If you didn't request this, please ignore this email.
    """
    
    try:
        message = f"Subject: {subject}\n\n{body}"
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, message)
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        raise


def send_password_reset_email(to_email, reset_link):
    """✅ TC_LOGIN_023: Send password reset email"""
    subject = "Password Reset Request"
    body = f"""
    You requested a password reset for your account.
    
    Click the link below to reset your password:
    {reset_link}
    
    This link expires in 24 hours.
    
    If you didn't request this, please ignore this email and your password will remain unchanged.
    """
    
    try:
        message = f"Subject: {subject}\n\n{body}"
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, message)
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        raise
