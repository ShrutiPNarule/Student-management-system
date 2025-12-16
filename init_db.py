"""
Database Initialization Script
Initializes roles and other base data
"""
from dotenv import load_dotenv
load_dotenv()
from db import get_connection

def init_roles():
    conn = get_connection()
    cur = conn.cursor()
    
    roles = [
        ("admin", "Administrator who manages student data"),
        ("auditor", "Auditor who monitors logs and deleted records"),
        ("student", "Student user with limited permissions"),
    ]
    
    try:
        for role_name, description in roles:
            cur.execute(
                "SELECT id FROM roles_master WHERE name = %s",
                (role_name,)
            )
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO roles_master (name) VALUES (%s)",
                    (role_name,)
                )
                print(f"✅ Created role: {role_name}")
            else:
                print(f"ℹ️  Role already exists: {role_name}")
        
        conn.commit()
        print("\n✅ Roles initialized successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error initializing roles: {e}")
    finally:
        cur.close()

if __name__ == "__main__":
    init_roles()
