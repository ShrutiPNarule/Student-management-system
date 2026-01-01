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

    # Find user with email
    email = "naruleshruti2004@gmail.com"
    cur.execute("SELECT id, name, email, role_id FROM users_master WHERE email = %s", (email,))
    user = cur.fetchone()

    if user:
        print(f"Found user: {user['name']} ({user['email']})")
        print(f"Current role_id: {user['role_id']}")
        print(f"User ID: {user['id']}\n")
        
        # Update to superadmin (RL0007)
        cur.execute(
            "UPDATE users_master SET role_id = %s WHERE email = %s",
            ("RL0007", email)
        )
        conn.commit()
        
        # Verify update
        cur.execute("SELECT id, name, email, role_id FROM users_master WHERE email = %s", (email,))
        updated_user = cur.fetchone()
        
        print(f"✅ User {updated_user['name']} is now SUPERADMIN")
        print(f"   Role ID: {updated_user['role_id']}")
        print(f"   Email: {updated_user['email']}")
    else:
        print(f"❌ User with email {email} not found in database")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        cur.close()
        conn.close()
