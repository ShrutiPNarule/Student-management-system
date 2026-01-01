import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        database=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)

    email = "shrutipnarule1410@gmail.com"
    cur.execute("""
        SELECT u.id, u.name, u.email, u.role_id, r.name as role_name
        FROM users_master u
        LEFT JOIN roles_master r ON u.role_id = r.id
        WHERE u.email = %s
    """, (email,))
    user = cur.fetchone()

    if user:
        print(f"Found user:")
        print(f"  ID: {user['id']}")
        print(f"  Name: {user['name']}")
        print(f"  Email: {user['email']}")
        print(f"  Role ID: {user['role_id']}")
        print(f"  Role Name: {user['role_name']}")
    else:
        print(f"❌ User with email {email} not found in database")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        cur.close()
        conn.close()
