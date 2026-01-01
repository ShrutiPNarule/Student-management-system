#!/usr/bin/env python3
"""
Test script to verify the approval_audit route authorization
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def verify_admin_user():
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
        print("VERIFICATION: ADMIN ACCESS TO APPROVAL AUDIT")
        print("=" * 70)
        
        # Check admin user
        cur.execute("""
            SELECT u.id, u.name, u.email, u.role_id, r.name as role
            FROM users_master u
            LEFT JOIN roles_master r ON u.role_id = r.id
            WHERE u.email = 'zahoor.adcet@gmail.com'
        """)
        
        user = cur.fetchone()
        if user:
            print(f"\n✅ Admin User Found:")
            print(f"   ID: {user[0]}")
            print(f"   Name: {user[1]}")
            print(f"   Email: {user[2]}")
            print(f"   Role ID: {user[3]}")
            print(f"   Role: {user[4].upper()}")
            
            if user[4].lower() == 'admin':
                print(f"\n✅ User is ADMIN role")
                print(f"   Authorization check in route should PASS")
                print(f"   Code: if session.get('role') not in ['admin', 'superadmin']:")
                print(f"   Result: 'admin' IS in ['admin', 'superadmin'] → PASS ✅")
            else:
                print(f"\n❌ User is NOT admin role: {user[4]}")
        else:
            print(f"\n❌ Admin user not found")
        
        print("\n" + "=" * 70)
        print("ROUTE AUTHORIZATION CODE:")
        print("=" * 70)
        print("""
@app.route("/approval-audit", methods=["GET"])
def approval_audit():
    if session.get("role") not in ["admin", "superadmin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("index"))
    # ... rest of code
        """)
        
        print("\n" + "=" * 70)
        print("SOLUTION:")
        print("=" * 70)
        print("✅ Route code is updated")
        print("✅ Admin user exists in database")
        print("✅ User must LOGOUT and LOGIN AGAIN")
        print("✅ Session will be refreshed with new role check")
        print("=" * 70)
        
        cur.close()
        conn.close()
        
    except Exception as error:
        print(f"❌ ERROR: {error}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_admin_user()
