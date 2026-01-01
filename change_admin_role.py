"""
Script to change admin role to Clerk
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def change_admin_role_to_clerk():
    try:
        conn = psycopg2.connect(
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            connect_timeout=5
        )
        cur = conn.cursor()
        print("[DB] Database connection established")
        
        # First, check if Clerk role exists, if not create it
        cur.execute("SELECT id FROM roles_master WHERE name = %s", ("clerk",))
        clerk_role = cur.fetchone()
        
        if not clerk_role:
            print("📝 Clerk role not found. Creating it...")
            cur.execute(
                "INSERT INTO roles_master (name) VALUES (%s) RETURNING id",
                ("clerk",)
            )
            clerk_role_id = cur.fetchone()[0]
            print(f"✅ Created Clerk role with ID: {clerk_role_id}")
        else:
            clerk_role_id = clerk_role[0]
            print(f"✅ Found existing Clerk role with ID: {clerk_role_id}")
        
        # Now find the admin user
        cur.execute("""
            SELECT u.id, u.name, r.name as current_role 
            FROM users_master u 
            LEFT JOIN roles_master r ON u.role_id = r.id 
            WHERE r.name = %s
        """, ("admin",))
        
        admin_users = cur.fetchall()
        
        if not admin_users:
            print("❌ No admin user found")
            cur.close()
            conn.close()
            return False
        
        # Update all admin users to clerk role
        for user_id, user_name, current_role in admin_users:
            cur.execute(
                "UPDATE users_master SET role_id = %s WHERE id = %s",
                (clerk_role_id, user_id)
            )
            print(f"✅ Changed role of user '{user_name}' (ID: {user_id}) from '{current_role}' to 'Clerk'")
        
        conn.commit()
        print("\n✅ Admin role successfully changed to Clerk!")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    change_admin_role_to_clerk()
