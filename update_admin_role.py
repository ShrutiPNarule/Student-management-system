#!/usr/bin/env python3
"""
Update Admin role permissions
Admin should ONLY have: View (reports), Log (activity), Approve (data)
Remove: Add, Delete, Marks, Change Role
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def update_admin_permissions():
    try:
        conn = psycopg2.connect(
            database=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        cur = conn.cursor()
        
        print("=" * 70)
        print("UPDATING ADMIN ROLE PERMISSIONS")
        print("=" * 70)
        
        # Get current admin role ID
        cur.execute("SELECT id FROM roles_master WHERE name = 'admin'")
        admin_role = cur.fetchone()
        
        if not admin_role:
            print("❌ Admin role not found!")
            cur.close()
            conn.close()
            return False
        
        admin_id = admin_role[0]
        print(f"\n📋 Admin Role ID: {admin_id}")
        
        # Get current permissions
        cur.execute("""
            SELECT 
                view_student, add_student, delete_student, add_marks,
                change_user_role, view_activity_log, create_application, 
                approve_application
            FROM roles_master 
            WHERE id = %s
        """, (admin_id,))
        
        current = cur.fetchone()
        print(f"\n📊 CURRENT PERMISSIONS:")
        print(f"   View Student: {current[0]}")
        print(f"   Add Student: {current[1]}")
        print(f"   Delete Student: {current[2]}")
        print(f"   Add Marks: {current[3]}")
        print(f"   Change Role: {current[4]}")
        print(f"   View Activity Log: {current[5]}")
        print(f"   Create Application: {current[6]}")
        print(f"   Approve Application: {current[7]}")
        
        # Update permissions
        cur.execute("""
            UPDATE roles_master 
            SET 
                view_student = TRUE,
                add_student = FALSE,
                delete_student = FALSE,
                add_marks = FALSE,
                change_user_role = FALSE,
                view_activity_log = TRUE,
                create_application = FALSE,
                approve_application = TRUE
            WHERE id = %s
        """, (admin_id,))
        
        conn.commit()
        
        print(f"\n✅ NEW PERMISSIONS (Updated):")
        print(f"   View Student (Reports): TRUE ✅")
        print(f"   Add Student: FALSE ❌")
        print(f"   Delete Student: FALSE ❌")
        print(f"   Add Marks: FALSE ❌")
        print(f"   Change Role: FALSE ❌")
        print(f"   View Activity Log: TRUE ✅")
        print(f"   Create Application: FALSE ❌")
        print(f"   Approve Application: TRUE ✅")
        
        # Get all admin users
        cur.execute("""
            SELECT id, email, name 
            FROM users_master 
            WHERE role_id = %s
        """, (admin_id,))
        
        admin_users = cur.fetchall()
        print(f"\n👥 AFFECTED ADMIN USERS: {len(admin_users)}")
        for user_id, email, name in admin_users:
            print(f"   • {name} ({email})")
        
        print("\n" + "=" * 70)
        print("✅ ADMIN ROLE PERMISSIONS UPDATED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📝 SUMMARY:")
        print("   Admin can now ONLY:")
        print("   ✅ View reports and analysis")
        print("   ✅ View activity logs")
        print("   ✅ Approve submitted data")
        print("\n   Admin CANNOT:")
        print("   ❌ Add students")
        print("   ❌ Delete students")
        print("   ❌ Add marks")
        print("   ❌ Change user roles")
        print("   ❌ Create applications")
        print("\n💡 NOTE: Clerk and Auditor roles remain unchanged")
        print("=" * 70)
        
        cur.close()
        conn.close()
        return True
        
    except Exception as error:
        print(f"❌ ERROR: {error}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    update_admin_permissions()
