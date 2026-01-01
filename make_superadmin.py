import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
try:
    conn = psycopg2.connect(
        database=os.getenv("DB_DATABASE"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Find user with ID ST000005
    cur.execute("SELECT id, name, email, role_id FROM users_master WHERE id = %s", ("ST000005",))
    user = cur.fetchone()

    if user:
        print(f"Found user: {user['name']} ({user['email']})")
        print(f"Current role_id: {user['role_id']}")
        
        # Update to superadmin (RL0007)
        cur.execute(
            "UPDATE users_master SET role_id = %s WHERE id = %s",
            ("RL0007", "ST000005")
        )
        conn.commit()
        
        # Verify update
        cur.execute("SELECT id, name, email, role_id FROM users_master WHERE id = %s", ("ST000005",))
        updated_user = cur.fetchone()
        
        print(f"✅ User {updated_user['name']} is now SUPERADMIN (role_id: {updated_user['role_id']})")
    else:
        print("❌ User ST000005 not found in database")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        cur.close()
        conn.close()
