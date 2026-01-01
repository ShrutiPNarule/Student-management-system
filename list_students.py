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

    # Get all users with ST prefix
    cur.execute("SELECT id, name, email, role_id FROM users_master WHERE id LIKE 'ST%' ORDER BY id")
    users = cur.fetchall()

    print(f"Total students found: {len(users)}\n")
    print("ID\t\tName\t\t\tEmail\t\t\t\tRole ID")
    print("=" * 100)
    
    for user in users:
        print(f"{user['id']}\t{user['name'][:20]:<20}\t{user['email'][:30]:<30}\t{user['role_id']}")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        cur.close()
        conn.close()
