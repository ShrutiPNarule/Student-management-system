"""
Give all admin rights to clerk role
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def give_admin_rights_to_clerk():
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
        
        # Step 1: Get admin role permissions
        cur.execute("""
            SELECT 
                view_student,
                add_student,
                delete_student,
                change_user_role,
                add_marks,
                view_activity_log,
                create_application,
                approve_application
            FROM roles_master 
            WHERE name = 'admin'
        """)
        
        admin_perms = cur.fetchone()
        
        if not admin_perms:
            print("❌ Admin role not found")
            cur.close()
            conn.close()
            return False
        
        print("📋 Current Admin Permissions:")
        view_st, add_st, del_st, chg_role, add_marks, view_log, create_app, approve_app = admin_perms
        print(f"   ✅ View Student: {view_st}")
        print(f"   ✅ Add Student: {add_st}")
        print(f"   ✅ Delete Student: {del_st}")
        print(f"   ❌ Change User Role: {chg_role}")
        print(f"   ✅ Add Marks: {add_marks}")
        print(f"   ✅ View Activity Log: {view_log}")
        print(f"   ❌ Create Application: {create_app}")
        print(f"   ❌ Approve Application: {approve_app}")
        
        # Step 2: Update clerk role with admin permissions
        print(f"\n🔄 Updating Clerk role with Admin permissions...")
        cur.execute("""
            UPDATE roles_master 
            SET 
                view_student = %s,
                add_student = %s,
                delete_student = %s,
                change_user_role = %s,
                add_marks = %s,
                view_activity_log = %s,
                create_application = %s,
                approve_application = %s
            WHERE name = 'clerk'
        """, (view_st, add_st, del_st, chg_role, add_marks, view_log, create_app, approve_app))
        
        conn.commit()
        
        print("   ✅ Clerk role updated successfully!")
        print("\n📋 Clerk now has the same permissions as Admin:")
        print(f"   ✅ View Student: {view_st}")
        print(f"   ✅ Add Student: {add_st}")
        print(f"   ✅ Delete Student: {del_st}")
        print(f"   ❌ Change User Role: {chg_role}")
        print(f"   ✅ Add Marks: {add_marks}")
        print(f"   ✅ View Activity Log: {view_log}")
        print(f"   ❌ Create Application: {create_app}")
        print(f"   ❌ Approve Application: {approve_app}")
        
        print("\n" + "="*60)
        print("✅ Successfully transferred all admin rights to clerk!")
        print("="*60)
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == "__main__":
    give_admin_rights_to_clerk()
