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

    print("ALL ROLES IN DATABASE:")
    print("=" * 60)
    cur.execute("SELECT id, name FROM roles_master ORDER BY id")
    roles = cur.fetchall()
    for role in roles:
        print(f"  ID: {role['id']:<10} | Name: '{role['name']}'")
    
    print()
    print("ADMIN ROLE SPECIFICALLY:")
    print("=" * 60)
    cur.execute("SELECT id, name FROM roles_master WHERE id = 'RL0002'")
    admin_role = cur.fetchone()
    if admin_role:
        print(f"  ID: {admin_role['id']}")
        print(f"  Name: '{admin_role['name']}'")
        print(f"  Lowercase: '{admin_role['name'].lower()}'")
        print(f"  Is 'admin'? {admin_role['name'].lower() == 'admin'}")
    else:
        print("❌ Admin role not found!")
    
    print()
    print("ADMIN USER:")
    print("=" * 60)
    cur.execute("""
        SELECT u.id, u.email, u.role_id, r.name as role_name
        FROM users_master u
        LEFT JOIN roles_master r ON u.role_id = r.id
        WHERE u.email = 'zahoor.adcet@gmail.com'
    """)
    user = cur.fetchone()
    if user:
        print(f"  Email: {user['email']}")
        print(f"  Role ID: {user['role_id']}")
        print(f"  Role Name: '{user['role_name']}'")
        print(f"  Lowercase: '{user['role_name'].lower() if user['role_name'] else 'NULL'}'")
    else:
        print("❌ Admin user not found!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    if 'conn' in locals() and conn:
        cur.close()
        conn.close()
