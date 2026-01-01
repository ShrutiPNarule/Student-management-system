"""
Script to change superadmin to admin and transfer all superadmin rights to admin role
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def transfer_superadmin_to_admin():
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
        print("[DB] Database connection established\n")
        
        # Step 1: Get superadmin role details
        cur.execute("""
            SELECT id, name, view_student, change_user_role 
            FROM roles_master 
            WHERE name = 'superadmin'
        """)
        superadmin_data = cur.fetchone()
        
        if not superadmin_data:
            print("❌ Superadmin role not found")
            cur.close()
            conn.close()
            return False
        
        superadmin_id, superadmin_name, view_student, change_role = superadmin_data
        print(f"📋 Found Superadmin role:")
        print(f"   - ID: {superadmin_id}")
        print(f"   - Permissions: view_student={view_student}, change_user_role={change_role}")
        
        # Step 2: Get admin role details
        cur.execute("""
            SELECT id FROM roles_master WHERE name = 'admin'
        """)
        admin_role = cur.fetchone()
        
        if not admin_role:
            print("❌ Admin role not found")
            cur.close()
            conn.close()
            return False
        
        admin_role_id = admin_role[0]
        print(f"\n📋 Found Admin role with ID: {admin_role_id}")
        
        # Step 3: Update admin role with superadmin permissions
        print(f"\n🔄 Transferring superadmin permissions to admin role...")
        cur.execute("""
            UPDATE roles_master 
            SET view_student = TRUE, change_user_role = TRUE
            WHERE name = 'admin'
        """)
        print("   ✅ Admin now has: view_student=TRUE, change_user_role=TRUE")
        
        # Step 4: Find all users with superadmin role
        cur.execute("""
            SELECT u.id, u.name 
            FROM users_master u 
            WHERE u.role_id = %s
        """, (superadmin_id,))
        
        superadmin_users = cur.fetchall()
        
        if superadmin_users:
            print(f"\n🔄 Converting superadmin users to admin...")
            for user_id, user_name in superadmin_users:
                cur.execute(
                    "UPDATE users_master SET role_id = %s WHERE id = %s",
                    (admin_role_id, user_id)
                )
                print(f"   ✅ Changed user '{user_name}' (ID: {user_id}) from superadmin to admin")
        else:
            print("\n✅ No superadmin users found to convert")
        
        # Step 5: Delete superadmin role
        print(f"\n🗑️  Removing superadmin role from system...")
        cur.execute("DELETE FROM roles_master WHERE name = 'superadmin'")
        print("   ✅ Superadmin role deleted")
        
        conn.commit()
        print("\n" + "="*60)
        print("✅ Successfully transferred superadmin to admin!")
        print("="*60)
        print("\n📝 Summary:")
        print("   - Admin role now has superadmin permissions")
        print("   - All superadmin users converted to admin")
        print("   - Superadmin role removed from system")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == "__main__":
    transfer_superadmin_to_admin()
