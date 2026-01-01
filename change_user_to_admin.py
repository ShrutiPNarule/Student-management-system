#!/usr/bin/env python3
"""
Change user zahoor.dcet@gmail.com from SUPERADMIN to ADMIN
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def change_user_role_to_admin():
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
        print("CHANGING USER ROLE TO ADMIN")
        print("=" * 70)
        
        # Get the user
        email = "zahoor.adcet@gmail.com"
        cur.execute("SELECT id, name, role_id FROM users_master WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if not user:
            print(f"\n❌ User with email {email} not found!")
            cur.close()
            conn.close()
            return False
        
        user_id, user_name, current_role_id = user
        print(f"\n👤 User Found:")
        print(f"   ID: {user_id}")
        print(f"   Name: {user_name}")
        print(f"   Email: {email}")
        print(f"   Current Role ID: {current_role_id}")
        
        # Get current role name
        cur.execute("SELECT name FROM roles_master WHERE id = %s", (current_role_id,))
        role_result = cur.fetchone()
        current_role = role_result[0] if role_result else "Unknown"
        print(f"   Current Role: {current_role.upper()}")
        
        # Get admin role ID
        cur.execute("SELECT id FROM roles_master WHERE name = 'admin'")
        admin_role = cur.fetchone()
        
        if not admin_role:
            print("\n❌ Admin role not found in database!")
            cur.close()
            conn.close()
            return False
        
        admin_role_id = admin_role[0]
        print(f"\n🔄 Changing to:")
        print(f"   New Role: ADMIN")
        print(f"   New Role ID: {admin_role_id}")
        
        # Update user role
        cur.execute("""
            UPDATE users_master 
            SET role_id = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (admin_role_id, user_id))
        
        conn.commit()
        
        print(f"\n✅ ROLE CHANGE SUCCESSFUL!")
        print(f"\n📊 ADMIN ROLE PERMISSIONS:")
        print(f"   ✅ View - See all student data & reports")
        print(f"   ✅ Log - View activity logs")
        print(f"   ✅ Approve - Approve auditor-verified data")
        print(f"   ❌ Add - Cannot add students")
        print(f"   ❌ Delete - Cannot delete students")
        print(f"   ❌ Marks - Cannot add marks")
        print(f"   ❌ Change Role - Cannot change roles")
        
        print(f"\n📋 User Details After Change:")
        cur.execute("SELECT id, name, email, role_id FROM users_master WHERE id = %s", (user_id,))
        updated_user = cur.fetchone()
        print(f"   ID: {updated_user[0]}")
        print(f"   Name: {updated_user[1]}")
        print(f"   Email: {updated_user[2]}")
        print(f"   Role ID: {updated_user[3]}")
        
        # Get role name
        cur.execute("SELECT name FROM roles_master WHERE id = %s", (updated_user[3],))
        new_role = cur.fetchone()[0]
        print(f"   Role: {new_role.upper()}")
        
        print("\n" + "=" * 70)
        print("✅ USER SUCCESSFULLY CHANGED TO ADMIN ROLE")
        print("=" * 70)
        print("\n💡 Next Steps:")
        print("   1. User needs to logout and login again")
        print("   2. Dropdown will now show only Admin permissions")
        print("   3. Menu will be updated to reflect Admin access level")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as error:
        print(f"\n❌ ERROR: {error}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    change_user_role_to_admin()
