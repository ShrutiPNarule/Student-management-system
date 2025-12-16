import smtplib

# ------------ EMAIL CONFIG (CHANGE THIS!) ------------

SMTP_SERVER = "smtp.gmail.com"      # or your provider
SMTP_PORT = 587
SENDER_EMAIL = "academic.techwork@gmail.com"      # change
SENDER_PASSWORD = "urjwuasqzoirpxot"      # change (app password, not normal password)


def send_otp_email(to_email, otp):
    subject = "Your Login OTP"
    body = f"Your OTP is {otp}. It is valid for 5 minutes."

    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, message)
