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

    # Check admin user
    email = "zahoor.adcet@gmail.com"
    cur.execute("""
        SELECT u.id, u.name, u.email, u.role_id, r.id as role_db_id, r.name as role_name
        FROM users_master u
        LEFT JOIN roles_master r ON u.role_id = r.id
        WHERE u.email = %s
    """, (email,))
    user = cur.fetchone()

    if user:
        print("=" * 60)
        print(f"USER FOUND: {user['name']}")
        print("=" * 60)
        print(f"Email: {user['email']}")
        print(f"User ID: {user['id']}")
        print(f"Role ID (FK): {user['role_id']}")
        print(f"Role Name from DB: {user['role_name']}")
        print(f"Role DB ID: {user['role_db_id']}")
        print()
        
        # Check if role_id is correct
        if user['role_id'] == 'RL0002':
            print("✅ Role ID is RL0002 (ADMIN) - Correct")
        else:
            print(f"❌ Role ID is {user['role_id']} - Should be RL0002")
        
        # Check role name
        if user['role_name'] and user['role_name'].lower() == 'admin':
            print(f"✅ Role Name is '{user['role_name']}' (lowercase: 'admin') - Correct")
        else:
            print(f"❌ Role Name is '{user['role_name']}' - Should be 'admin'")
        
        print()
        print("AUTH CHECK:")
        print(f"  Is role == 'admin'? {user['role_name'].lower() == 'admin' if user['role_name'] else False}")
        print(f"  Is role in ['admin', 'superadmin']? {user['role_name'].lower() in ['admin', 'superadmin'] if user['role_name'] else False}")
    else:
        print(f"❌ User with email {email} not found in database")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'conn' in locals() and conn:
        cur.close()
        conn.close()
