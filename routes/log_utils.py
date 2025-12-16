from db import get_connection
from flask import session

def log_action(action, details=""):
    user_email = session.get("user_email")
    role = session.get("role")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO activity_logs (user_email, role_name, action, details)
        VALUES (%s, %s, %s, %s)
        """,
        (user_email, role, action, details)
    )

    conn.commit()
    cur.close()
    conn.close()
