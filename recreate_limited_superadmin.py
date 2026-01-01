"""
Recreate superadmin role with LIMITED, CRITICAL permissions only
and revert admin to original permissions
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def recreate_superadmin_with_limited_access():
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
        
        # Step 1: Reset admin role to original permissions (without superadmin permissions)
        print("🔄 Step 1: Resetting Admin role to original permissions...")
        cur.execute("""
            UPDATE roles_master 
            SET change_user_role = FALSE
            WHERE name = 'admin'
        """)
        print("   ✅ Admin permissions reset:")
        print("      - Change User Role: ❌ (removed)")
        print("      - Keep: View, Add, Delete Students, Add Marks, View Activity Log")
        
        # Step 2: Check if superadmin role already exists
        cur.execute("SELECT id FROM roles_master WHERE name = 'superadmin'")
        superadmin_exists = cur.fetchone()
        
        if superadmin_exists:
            # Delete existing superadmin first
            print("\n🗑️  Removing old superadmin role...")
            cur.execute("DELETE FROM roles_master WHERE name = 'superadmin'")
            print("   ✅ Old superadmin role deleted")
        
        # Step 3: Create new LIMITED superadmin role with ONLY critical permissions
        print("\n✨ Step 2: Creating new LIMITED superadmin role with critical permissions only...")
        cur.execute("""
            INSERT INTO roles_master (
                name,
                view_student,
                add_student,
                delete_student,
                change_user_role,
                add_marks,
                view_activity_log,
                create_application,
                approve_application
            ) VALUES (
                'superadmin',
                FALSE,      -- No direct student viewing
                FALSE,      -- No adding students
                FALSE,      -- No deleting students
                TRUE,       -- ✅ CRITICAL: Change user roles
                FALSE,      -- No adding marks
                TRUE,       -- ✅ CRITICAL: View activity log (security)
                FALSE,      -- No creating applications
                TRUE        -- ✅ CRITICAL: Approve applications
            )
            RETURNING id
        """)
        
        superadmin_id = cur.fetchone()[0]
        print("   ✅ New superadmin role created with ID:", superadmin_id)
        print("\n   📋 Superadmin CRITICAL PERMISSIONS:")
        print("      ✅ Change User Role - Manage user access and permissions")
        print("      ✅ Approve Application - Make critical business decisions")
        print("      ✅ View Activity Log - Audit and security oversight")
        print("      ❌ All other permissions (no data overload)")
        
        # Step 4: Find the former superadmin user (Zahoorahmed Sayyad)
        cur.execute("""
            SELECT u.id, u.name 
            FROM users_master u 
            WHERE u.role_id = (SELECT id FROM roles_master WHERE name = 'admin')
            AND u.name = 'Zahoorahmed Sayyad'
        """)
        
        user_result = cur.fetchone()
        
        if user_result:
            user_id, user_name = user_result
            # Convert back to superadmin
            cur.execute(
                "UPDATE users_master SET role_id = %s WHERE id = %s",
                (superadmin_id, user_id)
            )
            print(f"\n👤 Step 3: User management...")
            print(f"   ✅ Converted '{user_name}' back to LIMITED superadmin role")
        else:
            print(f"\n👤 Step 3: No matching superadmin user found to convert back")
        
        conn.commit()
        print("\n" + "="*70)
        print("✅ Successfully recreated superadmin with LIMITED, CRITICAL access!")
        print("="*70)
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == "__main__":
    recreate_superadmin_with_limited_access()
